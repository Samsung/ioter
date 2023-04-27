#!/usr/bin/env python
import os
import fcntl
import pyudev
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

    def run(self):
        # Runs the actual loop to detect the events
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='usb')
        self.observer = pyudev.MonitorObserver(
            self.monitor, self.usb_Device_EventHandler)
        self.observer.start()

    def usb_Device_EventHandler(self, action, device):
        if device.action == 'add':
            time.sleep(1)  # wait for reading properties when insert dongle
            self.usb_changed.emit(device.action, device.device_path)
        elif device.action == 'remove':
            self.usb_changed.emit(device.action, device.device_path)

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
        if 'ID_VENDOR' not in device.properties:
            return False
        if "SAMSUNG" in device.properties['ID_VENDOR']:  # except samsung phone
            return False
        if path is not None:
            if device.properties['DEVPATH'].find(path) == -1:
                return False
            for usb_device in self.usb_devices:
                if path.find(usb_device.devpath) >= 0:
                    return False
        return True

    def add_device(self, path=None):
        self.context = pyudev.Context()
        for device in self.context.list_devices(subsystem='tty'):
            if self.is_usb_device(device, path):
                usb_device = UsbDevice(
                    device.device_node, device.properties['DEVPATH'], device.properties['ID_SERIAL_SHORT'], device.properties['ID_VENDOR'])
                self.set_devnum(usb_device)
                self.usb_devices.append(usb_device)
                # usb_device.item_display()
                if path is not None:
                    return usb_device.comPort
        return None

    def remove_device(self, path):
        path = path.partition('/tty')
        for usb_device in self.usb_devices:
            if path[0].find(usb_device.devpath) >= 0:
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
    def __init__(self, comPort, devpath, serial, vendor_name):
        '''
        ex : comPort : /dev/ttyACM0
             devpath : /devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.3/1-1.3:1.1/tty/ttyACM0
             serial : FFC5531D8BC2
             vendor_name : Nordic_Semiconductor
        '''
        self.comPort = comPort.split("/dev/")[1]                # ttyACM0
        # /devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.3/1-1.3:1.1
        self.devpath = devpath[:devpath.find('/tty')]
        # /devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.3
        self.devpath = self.devpath[:self.devpath.rfind('/')]
        self.serial = serial
        self.vendor_name = vendor_name
        self.devnum = -1
        self.usbpath = ""
        # /sys/devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.3/uevent
        if os.path.exists('/sys' + self.devpath+'/uevent'):
            file = open('/sys' + self.devpath+'/uevent', 'r')
            while True:
                line = file.readline()
                if not line:
                    break
                if line.find('DEVNAME=') >= 0:          # DEVNAME=bus/usb/001/053
                    self.usbpath = line.strip()
                    # /dev/bus/usb/001/053
                    self.usbpath = '/dev/' + self.usbpath[len('DEVNAME='):]

        # self.vendor_id = vendor_id
        # self.model_id = model_id
    def reset_device(self):
        USBDEVFS_RESET = 21780
        try:
            f = open(self.usbpath, 'w', os.O_WRONLY)
            fcntl.ioctl(f, USBDEVFS_RESET, 0)
            print('Successfully reset %s : %s' % (self.usbpath, self.comPort))
        except Exception as ex:
            print('Failed to reset device! Error: %s' % ex)

    def set_devnum(self, devnum):
        self.devnum = devnum

    def item_display(self):
        print('comPort = ' + self.comPort)
        print('devpath = ' + self.devpath)
        print('serial = ' + self.serial)
        print('vendor_name = ' + self.vendor_name)
        print('usbpath = ' + self.usbpath)
        print('devnum = ', self.devnum)

# def main():
#    test = Usb_manager(10)

# if __name__ == "__main__":
#    main()
