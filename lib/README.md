# Build OpenThread Shared Library 
The "build_ot" command builds several openthread libraries and installs them as libopenthread-{THREAD_DEVICE_TYPE}-shared.so.{OPENTHREAD_VER} in ./lib.


## How to build

These installation instructions have been tested on Ubuntu 22.04 LTS.

```
$ mkdir -p ~/ioter_src
$ cd ~/ioter_src
$ git clone https://github.com/Samsung/ioter.git
$ cd ioter
$ git submodule update --init

$ ./script/build_ot
```
### Thread Device Types
* fed - Full Thread End Device
* med - Minimal Thread End Device
* sed - Sleepy Thread End device

