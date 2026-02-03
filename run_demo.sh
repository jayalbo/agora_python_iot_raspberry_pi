#!/bin/bash
# Run demo with system Python (has GStreamer bindings)
# but include our local modules
cd /home/jay/test_agora
PYTHONPATH=/home/jay/test_agora /usr/bin/python3 demo_gst.py "$@"
