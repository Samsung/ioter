# Docker image support
You can use a Docker image that 'ioter' environment is prepared.

It confirmed that is working on below host OS:
- Ubuntu Lunar 23.04
- Ubuntu Jammy 22.04 (LTS)
- Ubuntu Focal 20.04 (LTS)
- Ubuntu Bionic 18.04 (LTS)

It also confirmed that there are unsupported host OS:
- Ubuntu Xenial 16.04
- macOS
- Any OS running on ARM platform such as Raspberry Pi

## How to start
There are things to be needed to prepare on host side.
1. Set xhost to connect to X server and use X11
> $ xhost +local:root

2. (For Ubuntu 23.04 only) Stop wireplumber service process that keep Bluetooth service running
> $ systemctl --user stop wireplumber

3. Turn off Bluetooth service
> $ systemctl stop bluetooth

or

> $ service bluetooth stop

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
- VERSION: ioter image version such as '0.1.0'. You can find details from https://hub.docker.com/r/spdkimo/ioter/tags
