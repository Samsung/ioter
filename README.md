# Ioter
## What is Ioter
Ioter is a tool that allows you to emulate all Matter supported IoT devices with Linux PC and Thread RCP dongle. This tool runs All-cluster-app of Matter on Linux PC to emulate multiple instances of Matter supported various IoT nodes. Each of these IoT nodes uses underlying Thread RCP based USB Dongle(Radio) for data transmission. By using Samsungs SmartThings Station(that acts as Border Router) and SmartThings Application along with emulated IoT nodes, we can configure a Smart Home.

Ioter acts as Mate/Helper to developers, testers and device manufacturers involved in smart home devices that are compliant with Matter and Thread specifications and it is very beneficial in terms of its below offerings: 

- **Flexibility:** Multiple types of IoT devices can be implemented using single RCP Dongle.
- **Multiple devices:** Devices can be implemented as many as the number of RCP dongles(up to 10).
- **Low Cost:** Do not need to pay for testing various IoT device types.
- **Time-Saving:** Time involved in searching and procuring various IoT device types is saved.
- **Easy to use:** Intuitive UI supports in controlling the status of various device types from the program window.
- **Automation:** Repeated testing through scripts can validate device stability and connection.

## Overview
![ioter_overview](https://github.com/Samsung/ioter/blob/main/res/doc/ioter_overview.png)

## Supporting Things (2023-04-27)

- Light Bulb
- Door Lock
- Contact Sensor
- Temperature Sensor
- Humidity Sensor
- Light Sensor
- Window Covering
- Occupancy Sensor
- OnOff Plugin
![Supporting Things (2023-04-27).png](https://github.com/Samsung/ioter/blob/main/res/doc/Supporting%20Things%20(2023-04-27).png)

## Prepare tools
- Bluetooth enabled desktop or laptop
- Ubuntu 22.04 (Previous version has Bluetooth version problem)
- USB hub with power input (USB3.0 recommended)
- Thread RCP usb dongle. We verified with this:
    1. **Nordic nrf52840** [OT RCP dongle guide](./docs/guides/README.md)   
    ![nordic_nrf52840_dongle](https://github.com/Samsung/ioter/blob/main/res/doc/nordic_nrf52840_dongle.png)
    2. **Nordic nrf52840-DK board** [OT RCP board guide](https://openthread.io/codelabs/openthread-hardware#3)   
    ![nrf52840dk](https://github.com/Samsung/ioter/blob/main/res/doc/nrf52840dk.png)
    3. **Silabs thunderBoardSense2** [OT RCP Silabs build&flash guide](https://docs.silabs.com/matter/2.0.0/matter-thread/matter-rcp)   
    ![Silabs_thunderBoardSense2](https://github.com/Samsung/ioter/blob/main/res/doc/silabs_thunderBoardSense2.png)
    4. **Silabs efr32-mighty-gecko-zigbee-and-thread-kit** [OT RCP Silabs build&flash guide](https://docs.silabs.com/matter/2.0.0/matter-thread/matter-rcp)   
    ![Silabs_efr32-mighty-gecko-zigbee-and-thread-kit](https://github.com/Samsung/ioter/blob/main/res/doc/efr32-mighty-gecko-starter-kit.png)
    5. **ESP32-H2-DevkitM-1** [OT RCP ESP build&run guide](https://docs.espressif.com/projects/esp-thread-br/en/latest/esp32/dev-guide/build_and_run.html)   
    ![ESP_esp32-h2-devkitm-1](https://github.com/Samsung/ioter/blob/main/res/doc/esp32-h2-devkitm-1.png)

- Samsung SmartThings with SmartThings hub or SmartThings Station / Apple Home app with Homepod2 or Homepod mini
![sam_app](https://github.com/Samsung/ioter/blob/main/res/doc/sam_app.png)

## How to install and excute
1. install
```
cd ioter
./script/setup
```
2. excute
```
cd ioter
./script/run
```
Or you can use [**Docker image**](https://github.com/Samsung/ioter/blob/main/docs/guides/DOCKER.md)

## How to onboarding
![guide1](https://github.com/Samsung/ioter/blob/main/res/doc/guide1.png)
1. If you run the ioter with run script, the main window will appear, and if you press the start button, the device control window will appear.
2. The power on button is the same as the power operation of the actual device.
3. In the App, click the add device button in the upper right corner.

![guide2](https://github.com/Samsung/ioter/blob/main/res/doc/guide2.png)

4. And with scan qr code, device onboarding can be started. (It can also be started with other options like pairing code or scanning for nearby device.)
5. When you click Power on (step 2), a QR code and a paring code are created. Use this to proceed with the onboarding procedure.

![guide3](https://github.com/Samsung/ioter/blob/main/res/doc/guide3.png)

6. When onboarding is completed, device control is possible.

## Known issues
### 1. Problem with specific linux kernel version (higher than 5.16 and lower than 6.1.2)
The message below appears in the syslog
kernel: wpan0 (unregistered): mctp_unregister: BUG mctp_ptr set for unknown type 65535

https://github.com/openthread/openthread/issues/8523

Please use a stable kernel version of 5.15.0-60-generic

```
$ sudo apt-get install aptitude
$ sudo aptitude search linux-image
$ sudo aptitude install linux-image-5.15.0-60-generic
$ sudo grub-mkconfig | grep -iE "menuentry 'Ubuntu, with Linux" | awk '{print i++ " : "$1, $2, $3, $4, $5, $6, $7}'
  ex)
    0 : menuentry 'Ubuntu, with Linux 5.19.0-32-generic' --class ubuntu
    1 : menuentry 'Ubuntu, with Linux 5.19.0-32-generic (recovery mode)'
    2 : menuentry 'Ubuntu, with Linux 5.15.0-60-generic' --class ubuntu
    3 : menuentry 'Ubuntu, with Linux 5.15.0-60-generic (recovery mode)'
$ sudo nano /etc/default/grub
   Find line GRUB_DEFAULT=...(by default GRUB_DEFAULT=0) and sets in quotes menu path to concrete Kernel. 
   In my system first index was 1 and second was 2. I set in to GRUB_DEFAULT
   GRUB_DEFAULT="1>2"
$ sudo update-grub
```
### 2. With Ubuntu 20.04.2 LTS(Focal Fossa) , there is a BLE connection issue while onboarding End Node. To use ioter please upgrade Ubuntu 22.04 LTS or later.
https://github.com/project-chip/connectedhomeip/issues/6347 

## Contributing

For Ioter contribution, see our [Contributing Guidelines](https://github.com/Samsung/ioter/blob/main/CONTRIBUTING.md) for more information.
We welcome your contribution at any time.
