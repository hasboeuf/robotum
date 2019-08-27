# robotboard

## Install (Ubuntu 18.04)

Not the right targeted OS for now.

```bash
deb [arch=amd64] http://www.linux-projects.org/listing/uv4l_repo/xenial xenial main
wget -q -O - http://www.linux-projects.org/listing/uv4l_repo/lpkey.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install uv4l uv4l-uvc uv4l-mjpegstream uv4l-dummy uv4l-xscreen uv4l-server uv4l-webrtc uv4l-x11-renderer uv4l-demos
```

## Run server

Dummy for now.

```bash
v4l --framerate 15 -f --auto-video_nr --driver xscreen --xorigin 0 --yorigin 0 --width 640 --height 480
```

## Run client

Echo WebRTC DataChannel for now.

```bash
python3 robotboard.py
```
