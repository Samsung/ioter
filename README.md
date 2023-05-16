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
![ioter_overview](https://user-images.githubusercontent.com/131251075/234764651-0662208c-3cc6-40b3-9999-9beab3db718a.JPG)

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

![ioter-things](https://user-images.githubusercontent.com/131251075/234766757-ec8cb1e9-4d6a-439e-bf78-cec875855e01.PNG)

## Prepare tools
- Bluetooth enabled desktop or laptop
- Ubuntu 22.04 (Previous version has Bluetooth version problem)
- USB hub with power input (USB3.0 recommended)
- Thread RCP usb dongle. We verified with this:
    1. **Nordic nrf52840** [OT RCP dongle guide](./docs/guides/README.md)   
    ![nordic_nrf52840_dongle](https://github.com/Samsung/ioter/assets/131251075/fe4f9fc3-077f-4cf1-8de3-56a64af69efa)

- Phone with SmartThings App installed and onboarded with Samsung SmartThings Station or SmartThings hub

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

## How to onboarding (with SmnartThings App)
![onbooadingGuide 1](https://github.com/Samsung/ioter/assets/131251075/200fd452-549a-4db8-ad7d-bfbd1fef5ebf)
1. If you run the ioter with run script, the main window will appear, and if you press the start button, the device control window will appear.
2. The power on button is the same as the power operation of the actual device.
3. In the SmartThings App, click the add device button in the upper right corner.   

![onbooadingGuide 2](https://github.com/Samsung/ioter/assets/131251075/ce292cc1-cc6e-48da-9827-1f673f66e545)

4. And with scan qr code, device onboarding can be started. (It can also be started with pairing code and scan nearby device.)
5. When you click Power on (step 2), a QR code and a paring code are created. Use this to proceed with the onboarding procedure.   

![onbooadingGuide 3](https://github.com/Samsung/ioter/assets/131251075/fccf8da9-020b-4b69-9e00-089488af1523)

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
