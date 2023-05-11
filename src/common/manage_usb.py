#!/usr/bin/env python
import os
import fcntl
#import pyudev
import glob
import usb.core
import usb.util
import usb1
import time
from PyQt5.QtCore import *
'''
current usb list
usb detect (add/remove)
reset usb device
'''


class UsbMonitor(QThread):
    usb_changed = pyqtSignal(str, str)

    # 초기화 메서드 구현
    def __init__(self):
        super().__init__()
        self.device_list = []

    def run(self):
        self.context = usb1.USBContext()
        self.idVendor = 6421
        self.observer = UsbDeviceObserver(self.idVendor)
        self.observer.set_event_handler(self.usb_Device_EventHandler)
        self.observer.start()

        #self.devices = list(usb.core.find(find_all=True, idVendor=6421)) #idVendor=6421 is Nordic
        #self.ttyUSBs = glob.glob('/dev/tty.usbmodem*')

        #print(self.ttyUSBs)
        #while True:
        #    new_devices = list(usb.core.find(find_all=True))
        #    if new_devices != self.devices:
        #        self.usb_Device_EventHandler(new_devices)
        #        self.devices = new_devices
        #        time.sleep(3)
        #    for device in self.devices:
        #        print(device.serial_number)
        #        print(device.idVendor)
        #        print(device.manufacturer)
        #        print(device.product)
        #        print(device.parent)
        
        # Runs the actual loop to detect the events
        #self.context = pyudev.Context()
        #self.monitor = pyudev.Monitor.from_netlink(self.context)
        #self.monitor.filter_by(subsystem='usb')
        #self.observer = pyudev.MonitorObserver(
        #    self.monitor, self.usb_Device_EventHandler)
        #self.observer.start()

    def usb_Device_EventHandler(self, event, device):
        print(device)
        if event == 'add':
            time.sleep(1)
            #device_serial = device.serial_number
            self.usb_changed.emit('add', None)
        elif event == 'remove':
            time.sleep(1)
            self.usb_changed.emit('remove', None)

        #print("22222")
        #if new_devices is not None:
        #    print("333333")
        #    if len(new_devices) > len(self.devices):
        #        time.sleep(1)  # wait for reading properties when insert dongle
        #        added_device = set(new_devices).difference(set(self.devices)).pop()
        #        self.usb_changed.emit('add', added_device.idProduct)
        #    elif len(new_devices) < len(self.devices):
        #        removed_device = set(self.devices).difference(set(new_devices)).pop()
        #        self.usb_changed.emit('remove', removed_device.idProduct)

    def stop(self):
        self.quit()


class UsbManager():
    def __init__(self, max_device_number):
        self.max_device_number = max_device_number
        self.usb_devices = []
        self.add_device()
        # for usb_device in self.usb_devices:
        # usb_device.item_display()
        if len(self.usb_devices) == 0:
            print('No USB Serial devices detected.')

    def is_usb_device(self, device, path=None):
        #if 'ID_VENDOR' not in device.properties:
        #    return False
        #if "SAMSUNG" in device.properties['ID_VENDOR']:  # except samsung phone
        #    return False

        #idVendor               : 0x04e8 232
        #idProduct              : 0x6860
        #bcdDevice              :  0x504 Device 5.04
        #iManufacturer          :    0x1 SAMSUNG
        #iProduct               :    0x2 SAMSUNG_Android
        #iSerialNumber          :    0x3 R3CTB0QCL8R
        print("1111111111111111111111111111111")
        #if path is not None:
        #    if device.serial_number == -1:
        #        return False
        #    for usb_device in self.usb_devices:
        #        if path.find(usb_device.idVendor) >= 0:
        #            return False
        return True

    def add_device(self, path=None):
        self.devices = usb.core.find(find_all=True, idVendor=6421)
        for device in self.devices:
            if self.is_usb_device(device, path):
                #usb_device = UsbDevice(
                #    device.device_node, device.properties['DEVPATH'], device.properties['ID_SERIAL_SHORT'], device.properties['ID_VENDOR'])
                deviceComport = "tty.usbmodem" + device.serial_number + "2"
                usb_device = UsbDevice(
                    deviceComport, device.serial_number, device.manufacturer)
                #print(device)
                #print(f'{deviceComport}  {device.serial_number}  {device.idVendor}')
                self.set_devnum(usb_device)
                self.usb_devices.append(usb_device)
                # usb_device.item_display()
                if path is not None:
                    return usb_device.comPort
        return None

    def remove_device(self, path):
        #path = path.partition('/tty')
        new_devices = usb.core.find(find_all=True, idVendor=6421)
        for usb_device in self.usb_devices:
            if usb_device.serial not in new_devices:
                self.usb_devices.remove(usb_device)
                return usb_device.comPort
        return None

    def find_device(self, path):
        result = ""
        path = path.partition('/tty')
        for usb_device in self.usb_devices:
            if path[0].find(usb_device.devpath) >= 0:
                return usb_device
        return None

    def set_devnum(self, new_device):
        num = list(range(self.max_device_number))
        for usb_device in self.usb_devices:
            if usb_device.vendor_name == new_device.vendor_name:
                num.remove(usb_device.devnum)
        # print('set devnum : %d - %s' %(num[0], new_device.comPort))
        new_device.set_devnum(num[0])

    def get_list(self):
        return self.usb_devices

    def reset_device(self, comPort):
        print('manage reset usb device :' + comPort)
        for usb_device in self.usb_devices:
            if usb_device.comPort == comPort:
                print('find usb device :' + comPort)
                usb_device.reset_device()
                break


class UsbDevice:
    def __init__(self, comPort, serial, vendor_name):
        '''
        ex : comPort : /dev/ttyACM0
             devpath : /devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.3/1-1.3:1.1/tty/ttyACM0 #to do
             serial : FFC5531D8BC2
             vendor_name : Nordic_Semiconductor
        '''
        self.comPort = comPort             # tty.usbmodem
        # /devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.3/1-1.3:1.1
        # self.devpath = devpath[:devpath.find('/tty')]
        # /devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.3
        # self.devpath = self.devpath[:self.devpath.rfind('/')]
        self.serial = serial
        self.vendor_name = vendor_name
        self.devnum = -1
        self.usbpath = ""
        # /sys/devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.3/uevent
        #if os.path.exists('/sys' + self.devpath+'/uevent'):
        #    file = open('/sys' + self.devpath+'/uevent', 'r')
        #    while True:
        #        line = file.readline()
        #        if not line:
        #            break
        #        if line.find('DEVNAME=') >= 0:          # DEVNAME=bus/usb/001/053
        #            self.usbpath = line.strip()
        #            # /dev/bus/usb/001/053
        #            self.usbpath = '/dev/' + self.usbpath[len('DEVNAME='):]

        # self.vendor_id = vendor_id
        # self.model_id = model_id
    #def reset_device(self):
    #    USBDEVFS_RESET = 21780
    #    try:
    #        f = open(self.usbpath, 'w', os.O_WRONLY)
    #        fcntl.ioctl(f, USBDEVFS_RESET, 0)
    #        print('Successfully reset %s : %s' % (self.usbpath, self.comPort))
    #    except Exception as ex:
    #        print('Failed to reset device! Error: %s' % ex)

    def set_devnum(self, devnum):
        self.devnum = devnum

    def item_display(self):
        print('comPort = ' + self.comPort)
        #print('devpath = ' + self.devpath)
        print('serial = ' + self.serial)
        print('vendor_name = ' + self.vendor_name)
        print('usbpath = ' + self.usbpath)
        print('devnum = ', self.devnum)



class UsbDeviceObserver:

    def __init__(self, idVendor):
        self.idVendor = idVendor
        self.last_devices = []
        self.current_devices = []
        self.event_handler = None

    def set_event_handler(self, event_handler):
        self.event_handler = event_handler

    def start(self):
        self.last_devices = self.get_connected_devices()
        while True:
            self.current_devices = self.get_connected_devices()
            for device in self.current_devices:
                if device not in self.last_devices:
                    if self.event_handler is not None:
                        self.event_handler("add", device)
            for device in self.last_devices:
                if device not in self.current_devices:
                    if self.event_handler is not None:
                        self.event_handler("remove", device)
            self.last_devices = self.current_devices
            time.sleep(1)

    def get_connected_devices(self):
        devices = []
        for device in usb.core.find(find_all = True, idVendor = self.idVendor):
            devices.append(device)
        return devices



# def main():
#    test = Usb_manager(10)

# if __name__ == "__main__":
#    main()
