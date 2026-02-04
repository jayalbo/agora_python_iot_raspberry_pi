"""
Python wrapper for Agora IoT/RTSA SDK
"""
import ctypes
import os
from ctypes import c_int, c_uint, c_uint8, c_uint16, c_uint32, c_char_p, c_void_p, c_size_t, CFUNCTYPE, POINTER, Structure

# Load the SDK
SDK_PATH = "/home/jay/dev/agora_iot/agora-sdk/libagora-rtc-sdk.so"
if not os.path.exists(SDK_PATH):
    raise RuntimeError(f"SDK not found at {SDK_PATH}")

sdk = ctypes.CDLL(SDK_PATH)

# Type definitions
connection_id_t = c_uint32

# Enums
VIDEO_DATA_TYPE_YUV420 = 0
VIDEO_DATA_TYPE_H264 = 2
VIDEO_DATA_TYPE_H265 = 3
VIDEO_DATA_TYPE_GENERIC = 6
VIDEO_DATA_TYPE_GENERIC_JPEG = 20

VIDEO_FRAME_AUTO_DETECT = 0
VIDEO_FRAME_KEY = 3
VIDEO_FRAME_DELTA = 4

VIDEO_STREAM_HIGH = 0
VIDEO_STREAM_LOW = 1

# Structures
class video_frame_info_t(Structure):
    _fields_ = [
        ("data_type", c_int),      # video_data_type_e
        ("stream_type", c_int),    # video_stream_type_e
        ("frame_type", c_int),     # video_frame_type_e
        ("frame_rate", c_uint16),  # video_frame_rate_e
        ("rotation", c_int),       # video_orientation_e
    ]

class rtc_service_option_t(Structure):
    _fields_ = [
        ("area_code", c_uint32),
        ("product_id", c_char_p),
        ("log_cfg_log_disable", c_int),
        ("log_cfg_log_level", c_int),
        ("log_cfg_log_path", c_char_p),
        ("log_cfg_log_size", c_int),
    ]

class rtc_channel_options_t(Structure):
    _fields_ = [
        ("auto_subscribe_audio", c_int),
        ("auto_subscribe_video", c_int),
        ("subscribe_local_user", c_int),
        ("enable_audio_jitter_buffer", c_int),
        ("enable_audio_mixer", c_int),
        ("audio_codec_type", c_int),
        ("audio_jitter_frame_num", c_int),
    ]

# Callback function types
ON_JOIN_CHANNEL = CFUNCTYPE(None, connection_id_t, c_uint32, c_int)
ON_RECONNECTING = CFUNCTYPE(None, connection_id_t)
ON_CONNECTION_LOST = CFUNCTYPE(None, connection_id_t)
ON_REJOIN_CHANNEL = CFUNCTYPE(None, connection_id_t, c_uint32, c_int)
ON_LICENSE_FAIL = CFUNCTYPE(None, connection_id_t, c_int)
ON_ERROR = CFUNCTYPE(None, connection_id_t, c_int, c_char_p)
ON_USER_JOINED = CFUNCTYPE(None, connection_id_t, c_uint32, c_int)
ON_USER_OFFLINE = CFUNCTYPE(None, connection_id_t, c_uint32, c_int)
ON_USER_MUTE_AUDIO = CFUNCTYPE(None, connection_id_t, c_uint32, c_int)
ON_USER_MUTE_VIDEO = CFUNCTYPE(None, connection_id_t, c_uint32, c_int)
ON_AUDIO_DATA = CFUNCTYPE(None, connection_id_t, c_uint32, c_uint16, c_void_p, c_size_t, c_void_p)
ON_MIXED_AUDIO = CFUNCTYPE(None, connection_id_t, c_void_p, c_size_t, c_void_p)
ON_VIDEO_DATA = CFUNCTYPE(None, connection_id_t, c_uint32, c_uint16, c_void_p, c_size_t, POINTER(video_frame_info_t))
ON_TARGET_BITRATE = CFUNCTYPE(None, connection_id_t, c_uint32)
ON_KEY_FRAME_GEN_REQ = CFUNCTYPE(None, connection_id_t, c_uint32, c_int)
ON_TOKEN_EXPIRE = CFUNCTYPE(None, connection_id_t, c_char_p)
ON_MEDIA_CTRL = CFUNCTYPE(None, connection_id_t, c_uint32, c_void_p, c_size_t)
ON_RDT_STATE = CFUNCTYPE(None, connection_id_t, c_uint32, c_int)
ON_RDT_MSG = CFUNCTYPE(None, connection_id_t, c_uint32, c_int, c_void_p, c_size_t)

class agora_rtc_event_handler_t(Structure):
    _fields_ = [
        ("on_join_channel_success", ON_JOIN_CHANNEL),
        ("on_reconnecting", ON_RECONNECTING),
        ("on_connection_lost", ON_CONNECTION_LOST),
        ("on_rejoin_channel_success", ON_REJOIN_CHANNEL),
        ("on_license_validation_failure", ON_LICENSE_FAIL),
        ("on_error", ON_ERROR),
        ("on_user_joined", ON_USER_JOINED),
        ("on_user_offline", ON_USER_OFFLINE),
        ("on_user_mute_audio", ON_USER_MUTE_AUDIO),
        ("on_user_mute_video", ON_USER_MUTE_VIDEO),
        ("on_audio_data", ON_AUDIO_DATA),
        ("on_mixed_audio_data", ON_MIXED_AUDIO),
        ("on_video_data", ON_VIDEO_DATA),
        ("on_target_bitrate_changed", ON_TARGET_BITRATE),
        ("on_key_frame_gen_req", ON_KEY_FRAME_GEN_REQ),
        ("on_token_privilege_will_expire", ON_TOKEN_EXPIRE),
        ("on_media_ctrl_msg", ON_MEDIA_CTRL),
        ("on_rdt_state", ON_RDT_STATE),
        ("on_rdt_msg", ON_RDT_MSG),
    ]

# Function signatures
sdk.agora_rtc_init.argtypes = [c_char_p, POINTER(agora_rtc_event_handler_t), POINTER(rtc_service_option_t)]
sdk.agora_rtc_init.restype = c_int

sdk.agora_rtc_fini.argtypes = []
sdk.agora_rtc_fini.restype = c_int

sdk.agora_rtc_create_connection.argtypes = [POINTER(connection_id_t)]
sdk.agora_rtc_create_connection.restype = c_int

sdk.agora_rtc_destroy_connection.argtypes = [connection_id_t]
sdk.agora_rtc_destroy_connection.restype = c_int

sdk.agora_rtc_join_channel.argtypes = [connection_id_t, c_char_p, c_uint32, c_char_p, POINTER(rtc_channel_options_t)]
sdk.agora_rtc_join_channel.restype = c_int

sdk.agora_rtc_leave_channel.argtypes = [connection_id_t]
sdk.agora_rtc_leave_channel.restype = c_int

sdk.agora_rtc_send_video_data.argtypes = [connection_id_t, c_void_p, c_size_t, POINTER(video_frame_info_t)]
sdk.agora_rtc_send_video_data.restype = c_int


class AgoraIoTClient:
    """Simple wrapper for Agora IoT SDK"""
    
    def __init__(self, app_id: str):
        self.app_id = app_id.encode('utf-8')
        self.conn_id = connection_id_t(0)
        self.joined = False
        self._callbacks = None  # Keep reference to prevent GC
        self._handler = None
        self.on_key_frame_request = None  # User callback for keyframe requests
        
    def _default_callbacks(self):
        """Create default callback handlers"""
        def on_join(conn_id, uid, elapsed):
            print(f"Joined channel: uid={uid}, elapsed={elapsed}ms")
            self.joined = True
            
        def on_reconnecting(conn_id):
            print("Reconnecting...")
            
        def on_connection_lost(conn_id):
            print("Connection lost!")
            self.joined = False
            
        def on_rejoin(conn_id, uid, elapsed):
            print(f"Rejoined: uid={uid}")
            self.joined = True
            
        def on_license_fail(conn_id, err):
            print(f"License error: {err}")
            
        def on_error(conn_id, code, msg):
            msg_str = msg.decode('utf-8') if msg else "Unknown"
            print(f"Error: code={code}, msg={msg_str}")
            
        def on_user_joined(conn_id, uid, elapsed):
            print(f"User joined: uid={uid}")
            
        def on_user_offline(conn_id, uid, reason):
            print(f"User offline: uid={uid}")
            
        def on_key_frame_req(conn_id, uid, stream):
            if self.on_key_frame_request:
                self.on_key_frame_request()
            
        def on_target_bitrate(conn_id, bps):
            pass  # Silent
        
        # Store ALL callbacks to prevent GC
        self._callbacks = {
            'join': ON_JOIN_CHANNEL(on_join),
            'reconnecting': ON_RECONNECTING(on_reconnecting),
            'conn_lost': ON_CONNECTION_LOST(on_connection_lost),
            'rejoin': ON_REJOIN_CHANNEL(on_rejoin),
            'license_fail': ON_LICENSE_FAIL(on_license_fail),
            'error': ON_ERROR(on_error),
            'user_joined': ON_USER_JOINED(on_user_joined),
            'user_offline': ON_USER_OFFLINE(on_user_offline),
            'key_frame': ON_KEY_FRAME_GEN_REQ(on_key_frame_req),
            'target_bps': ON_TARGET_BITRATE(on_target_bitrate),
        }
        
        return agora_rtc_event_handler_t(
            on_join_channel_success=self._callbacks['join'],
            on_reconnecting=self._callbacks['reconnecting'],
            on_connection_lost=self._callbacks['conn_lost'],
            on_rejoin_channel_success=self._callbacks['rejoin'],
            on_license_validation_failure=self._callbacks['license_fail'],
            on_error=self._callbacks['error'],
            on_user_joined=self._callbacks['user_joined'],
            on_user_offline=self._callbacks['user_offline'],
            on_key_frame_gen_req=self._callbacks['key_frame'],
            on_target_bitrate_changed=self._callbacks['target_bps'],
        )
    
    def init(self):
        """Initialize the SDK"""
        self._handler = self._default_callbacks()
        ret = sdk.agora_rtc_init(self.app_id, ctypes.byref(self._handler), None)
        if ret != 0:
            raise RuntimeError(f"Failed to init SDK: {ret}")
        print("SDK initialized")
        return ret
    
    def create_connection(self):
        """Create a connection"""
        ret = sdk.agora_rtc_create_connection(ctypes.byref(self.conn_id))
        if ret != 0:
            raise RuntimeError(f"Failed to create connection: {ret}")
        print(f"Connection created: {self.conn_id.value}")
        return self.conn_id.value
    
    def join_channel(self, channel: str, uid: int, token: str = ""):
        """Join a channel"""
        channel_b = channel.encode('utf-8')
        token_b = token.encode('utf-8') if token else None
        
        # Pass NULL for options to use defaults
        ret = sdk.agora_rtc_join_channel(self.conn_id, channel_b, uid, token_b, None)
        if ret != 0:
            raise RuntimeError(f"Failed to join channel: {ret}")
        print(f"Joining channel: {channel}")
        return ret
    
    def send_video_jpeg(self, jpeg_data: bytes, frame_rate: int = 30):
        """Send JPEG video frame"""
        info = video_frame_info_t()
        info.data_type = VIDEO_DATA_TYPE_GENERIC_JPEG
        info.stream_type = VIDEO_STREAM_HIGH
        info.frame_type = VIDEO_FRAME_KEY  # JPEG frames are always keyframes
        info.frame_rate = frame_rate
        info.rotation = 0
        
        data_ptr = ctypes.cast(jpeg_data, c_void_p)
        ret = sdk.agora_rtc_send_video_data(self.conn_id, data_ptr, len(jpeg_data), ctypes.byref(info))
        return ret
    
    def send_video_h264(self, h264_data: bytes, is_keyframe: bool = False, frame_rate: int = 30):
        """Send H.264 video frame"""
        info = video_frame_info_t()
        info.data_type = VIDEO_DATA_TYPE_H264
        info.stream_type = VIDEO_STREAM_HIGH
        info.frame_type = VIDEO_FRAME_KEY if is_keyframe else VIDEO_FRAME_DELTA
        info.frame_rate = frame_rate
        info.rotation = 0
        
        data_ptr = ctypes.cast(h264_data, c_void_p)
        ret = sdk.agora_rtc_send_video_data(self.conn_id, data_ptr, len(h264_data), ctypes.byref(info))
        return ret
    
    def leave_channel(self):
        """Leave the channel"""
        ret = sdk.agora_rtc_leave_channel(self.conn_id)
        self.joined = False
        return ret
    
    def destroy_connection(self):
        """Destroy the connection"""
        return sdk.agora_rtc_destroy_connection(self.conn_id)
    
    def fini(self):
        """Cleanup the SDK"""
        return sdk.agora_rtc_fini()


