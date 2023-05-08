# Build OpenThread Shared Library 
The "build_ot" command builds an openthread library (i.e libopenthread-cli.so) and installs it as libopenthread-cli.so.${OPENTHREAD_VER}-{THREAD_DEVICE_TYPE} in ./lib.


## How to build

These installation instructions have been tested on Ubuntu 22.04 LTS.

```
$ mkdir -p ~/ioter_src
$ cd ~/ioter_src
$ git clone https://github.com/Samsung/ioter.git
$ cd ioter
$ git submodule update --init

# build fed : ./script/build_ot fed
# build med : ./script/build_ot med
# build sed : ./script/build_ot sed
$ ./script/build_ot fed/med/sed
```
### Thread Device Types
* fed - Full Thread End Device
* med - Minimal Thread End Device
* sed - Sleepy Thread End device

