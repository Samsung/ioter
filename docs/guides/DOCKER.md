# Docker image support

A Docker image with the ioter environment pre-prepared is available for use.

The following host operating systems are supported:
- Ubuntu Lunar 23.04
- Ubuntu Jammy 22.04 (LTS)
- Ubuntu Focal 20.04 (LTS)
- Ubuntu Bionic 18.04 (LTS)

The following host operating systems are *unsupported*, but may work:
- Ubuntu Xenial 16.04
- macOS
- Any OS running on ARM platform such as Raspberry Pi

## Configure the host

Begin by preparing the host side.

1. Set xhost to connect to X server and use X11:
`$ xhost +local:root`

2. (For Ubuntu 23.04 only) Stop the wireplumber service process that keeps the Bluetooth service running:
`$ systemctl --user stop wireplumber`

3. Turn off the Bluetooth service:
`$ systemctl stop bluetooth`

or

`$ service bluetooth stop`

## Run the Docker container

Run with the command below:
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
Where:
- `HOST_IOTER_PATH`: Path of the ioter repository on the host pc.
- `DEVICE_NODE_PATH`: Path of the device node. For example, most devices start with 'dev/ttyACM'.
- `VERSION`: The ioter image version, such as '0.1.0'. Find details at https://hub.docker.com/r/spdkimo/ioter/tags
