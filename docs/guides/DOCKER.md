# Docker image support
You can use a Docker image that 'ioter' environment is prepared.

It confirmed that is working on below host OS:
- Ubuntu 20.04

It also confirmed that there are unsupported host OS:
- Ubuntu 16.04
- macOS
- Any OS running on ARM platform such as Raspberry Pi

## How to start
There are things to be needed to prepare on host side.
1. Set xhost to connect to X server and use X11
> $ xhost +local:root

2. Turn off Bluetooth service
> systemctl stop Bluetooth

or

> service bluetooth stop

## Run docker container
You can run with below command.
```
sudo docker run --rm -it -e DISPLAY=$DISPLAY \
-v [HOST_IOTER_PATH]:/home/iot/ioter \
-v /tmp/.X11-unix:/tmp/.X11-unix \
-v "$HOME/.Xauthority:/root/.Xauthority:ro" \
--device=[DEVICE_NODE_PATH] \
-v /dev:/dev \
--privileged \
--net=host \
--cap-add=NET_ADMIN --cap-add=SYS_ADMIN \
docker.io/spdkimo/ioter:[VERSION] \
python3 ioter/src/main.py
```
- HOST_IOTER_PATH: Path of ioter repository on host pc
- DEVICE_NODE_PATH: Path of device node. For example, most devices starts with 'dev/ttyACM'
- VERSION: ioter image version. You can find details from https://hub.docker/repository/docker/spdkimo/ioter/
