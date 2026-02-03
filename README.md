# Agora IoT Video Streaming for Raspberry Pi

Stream live video from a Raspberry Pi camera to Agora channels using the IoT/RTSA SDK.

## Features

- GStreamer-based H.264 encoding
- Python wrapper for Agora IoT SDK
- Optimized for ARM64 (Raspberry Pi)
- ~30 FPS streaming

## Requirements

- Raspberry Pi (ARM64)
- Python 3.x
- GStreamer with x264 encoder
- Agora IoT SDK (`/home/jay/dev/agora_iot/agora-sdk/`)

## Installation

```bash
# GStreamer dependencies (if not installed)
sudo apt install gstreamer1.0-tools gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly python3-gi
```

## Usage

```bash
./run_demo.sh --appId=YOUR_APP_ID --channelId=CHANNEL_NAME --userId=USER_ID
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--appId` | required | Agora App ID |
| `--channelId` | required | Channel name to join |
| `--userId` | auto | User ID (0 = auto-generate) |
| `--device` | /dev/video0 | Camera device |
| `--width` | 640 | Video width |
| `--height` | 240 | Video height |
| `--fps` | 30 | Frame rate |
| `--bitrate` | 1000 | Video bitrate (kbps) |
| `--duration` | 0 | Duration in seconds (0 = infinite) |

### Examples

```bash
# Basic usage
./run_demo.sh --appId=YOUR_APP_ID --channelId=test

# Higher resolution
./run_demo.sh --appId=YOUR_APP_ID --channelId=test --width=1280 --height=720 --bitrate=2000

# Run for 60 seconds
./run_demo.sh --appId=YOUR_APP_ID --channelId=test --duration=60
```

## Files

- `run_demo.sh` - Launcher script
- `demo_gst.py` - Main demo (GStreamer + Agora)
- `agora_iot_wrapper.py` - Python wrapper for Agora IoT SDK

## License

MIT
