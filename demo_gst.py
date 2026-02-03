#!/usr/bin/env python3
"""
Agora Video Streaming Demo using GStreamer for H.264 encoding
This matches the working C implementation.
"""
import argparse
import signal
import sys
import time
import threading

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

from agora_iot_wrapper import AgoraIoTClient, VIDEO_DATA_TYPE_H264


class GstVideoStreamer:
    def __init__(self, app_id: str, channel_id: str, user_id: int = 0):
        self.client = AgoraIoTClient(app_id)
        self.channel_id = channel_id
        self.user_id = user_id or int(time.time()) % 100000
        self.pipeline = None
        self.main_loop = None
        self.running = False
        self.frame_count = 0
        self.start_time = 0
        self.fps = 30
        
    def start_agora(self):
        """Initialize and connect to Agora"""
        print("Initializing Agora SDK...")
        self.client.init()
        self.client.create_connection()
        
        print(f"Joining channel: {self.channel_id}")
        self.client.join_channel(self.channel_id, self.user_id)
        
        for _ in range(30):
            if self.client.joined:
                break
            time.sleep(0.1)
        
        if not self.client.joined:
            raise RuntimeError("Failed to join channel")
            
        print(f"Connected as user {self.user_id}")
        return True

    def on_new_sample(self, sink):
        """Callback when new H.264 frame is ready"""
        sample = sink.emit("pull-sample")
        if sample:
            buffer = sample.get_buffer()
            success, map_info = buffer.map(Gst.MapFlags.READ)
            if success:
                h264_data = bytes(map_info.data)
                
                # Check if this is a keyframe (NAL type 5 = IDR, 7 = SPS, 8 = PPS)
                is_keyframe = False
                if len(h264_data) > 4:
                    for i in range(min(len(h264_data) - 4, 100)):
                        if h264_data[i:i+4] == b'\x00\x00\x00\x01':
                            nal_type = h264_data[i+4] & 0x1F
                            if nal_type in (5, 7, 8):
                                is_keyframe = True
                                break
                
                # Send to Agora
                self.client.send_video_h264(h264_data, is_keyframe=is_keyframe, frame_rate=self.fps)
                
                self.frame_count += 1
                if self.frame_count % self.fps == 0:
                    elapsed = time.time() - self.start_time
                    actual_fps = self.frame_count / elapsed
                    kf = " [KEY]" if is_keyframe else ""
                    print(f"  {self.frame_count} frames ({actual_fps:.1f} FPS, {len(h264_data)} bytes){kf}")
                
                buffer.unmap(map_info)
            sample = None
            return Gst.FlowReturn.OK
        return Gst.FlowReturn.ERROR

    def build_pipeline(self, device: str, width: int, height: int, fps: int, bitrate: int):
        """Build GStreamer pipeline matching working C code"""
        self.fps = fps
        
        # Pipeline: v4l2src -> capsfilter -> jpegdec -> videoconvert -> x264enc -> appsink
        pipeline_str = (
            f'v4l2src device={device} ! '
            f'image/jpeg,width={width},height={height},framerate={fps}/1 ! '
            f'jpegdec ! '
            f'videoconvert ! '
            f'x264enc name=enc bitrate={bitrate} key-int-max={fps} speed-preset=5 tune=zerolatency byte-stream=true ! '
            f'video/x-h264,stream-format=byte-stream ! '
            f'appsink name=sink emit-signals=true sync=false'
        )
        
        print(f"Pipeline: {width}x{height} @ {fps}fps, {bitrate}kbps")
        
        self.pipeline = Gst.parse_launch(pipeline_str)
        
        # Connect to appsink
        sink = self.pipeline.get_by_name("sink")
        sink.connect("new-sample", self.on_new_sample)
        
        return True

    def stream(self, duration: int = 0):
        """Run the streaming pipeline"""
        self.running = True
        self.frame_count = 0
        self.start_time = time.time()
        
        print("\nStreaming... Press Ctrl+C to stop\n")
        
        # Start pipeline
        self.pipeline.set_state(Gst.State.PLAYING)
        
        # Run main loop
        self.main_loop = GLib.MainLoop()
        
        # Handle duration
        if duration > 0:
            GLib.timeout_add_seconds(duration, self.stop)
        
        try:
            self.main_loop.run()
        except:
            pass
        
        elapsed = time.time() - self.start_time
        print(f"\nTotal: {self.frame_count} frames in {elapsed:.1f}s ({self.frame_count/max(1,elapsed):.1f} FPS)")

    def stop(self):
        """Stop streaming"""
        self.running = False
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
        if self.main_loop:
            self.main_loop.quit()
        return False  # Don't repeat timeout

    def cleanup(self):
        """Release resources"""
        self.stop()
        self.client.leave_channel()
        self.client.destroy_connection()
        self.client.fini()
        print("Cleanup complete")


def main():
    Gst.init(None)
    
    parser = argparse.ArgumentParser(
        description="Agora Video Streaming Demo (GStreamer H.264)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--appId", required=True, help="Agora App ID")
    parser.add_argument("--channelId", required=True, help="Channel name")
    parser.add_argument("--userId", type=int, default=0, help="User ID (0=auto)")
    parser.add_argument("--device", default="/dev/video0", help="Camera device")
    parser.add_argument("--width", type=int, default=640, help="Video width")
    parser.add_argument("--height", type=int, default=240, help="Video height")
    parser.add_argument("--fps", type=int, default=30, help="Frame rate")
    parser.add_argument("--bitrate", type=int, default=1000, help="Video bitrate (kbps)")
    parser.add_argument("--duration", type=int, default=0, help="Duration (0=infinite)")
    
    args = parser.parse_args()
    
    streamer = GstVideoStreamer(args.appId, args.channelId, args.userId)
    
    def signal_handler(sig, frame):
        print("\nStopping...")
        streamer.stop()
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        streamer.start_agora()
        streamer.build_pipeline(args.device, args.width, args.height, args.fps, args.bitrate)
        streamer.stream(args.duration)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        streamer.cleanup()


if __name__ == "__main__":
    main()
