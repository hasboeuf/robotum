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

## Dumb inputs test

This is using `keyboard` package which requires root access.

```bash
pip3 install -r requirements.txt
sudo ~/.virtualenvs/robotum/bin/python3 robotboard/input.py
```

## Service

```bash
sudo apt-get install python-dev python-rpi.gpio
sudo mkdir -p /var/log/robot
sudo chown $USER:$USER /var/log/robot
sudo ln -s $(pwd)/robot_on_start /usr/bin/robot_on_start
sudo cp service/robot.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable robot.service
```
