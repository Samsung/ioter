# ioter-ui-app - lib

## How to build

These installation instructions have been tested on Ubuntu 22.04 LTS.

```
$ mkdir -p ~/ioter_src
$ cd ~/ioter_src
$ git clone https://github.ecodesamsung.com/THREAD/ioter-ui-app.git
$ cd ioter-ui-app
$ git submodule update --init

# build fed : ./script/build_ot fed
# build med : ./script/build_ot med
# build sed : ./script/build_ot sed
$ ./script/build_ot fed/med/sed
```

The "build_ot" command builds an openthread library (i.e libopenthread-cli.so) and installs it as libopenthread-cli.so.${OPENTHREAD_VER}-build in ./lib.
