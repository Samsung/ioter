# Build Chip-all-clusters-app for Matter

The "build_ioter" command builds a chip-all-clusters-app executable and installs it in ./bin. This executable emulates Matter End node applications like LightBulb,Door Lock,etc. on top of thread usb dongle.


## How to build

These installation instructions have been tested on Ubuntu 22.04 LTS.

```
$ mkdir -p ~/ioter_src
$ cd ~/ioter_src
$ git clone https://github.com/Samsung/ioter.git
$ cd ioter
$ git submodule update --init

# build fed : ./script/build_ioter fed
# build med : ./script/build_ioter med
# build sed : ./script/build_ioter sed
$ ./script/build_ioter fed/med/sed
```
### Thread Device Types
* fed - Full Thread End Device
* med - Minimal Thread End Device
* sed - Sleepy Thread End device
