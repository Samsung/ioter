#BSD 3-Clause License
#
#Copyright (c) 2023, Samsung Electronics Co.
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the
#   names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#POSSIBILITY OF SUCH DAMAGE.
#
###########################################################################
# File : manage_use.py
# Description: Manage usb devices and operations
# e.g. current usb list, usb detect (add/remove), reset usb device

from common.log import Log

import os
import fcntl
import pyudev
import time
from PyQt5.QtCore import *

## USB monitor class ##
class UsbMonitor(QThread):
    usb_changed = pyqtSignal(str, str)

    ## Init new thread ##
    def __init__(self):
        super().__init__()

    ## Runs the actual loop to detect the events ##
    def run(self):
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='usb')
        self.observer = pyudev.MonitorObserver(
            self.monitor, self.usb_Device_EventHandler)
        self.observer.start()

    ## USB device event handler ##
    def usb_Device_EventHandler(self, action, device):
        if device.action == 'add':
            time.sleep(1)  # wait for reading properties when insert dongle
            self.usb_changed.emit(device.action, device.device_path)
        elif device.action == 'remove':
            self.usb_changed.emit(device.action, device.device_path)

    ## Stop thread ##
    def stop(self):
        self.quit()

## USB manager class ##
class UsbManager():
    ## Init class ##
    def __init__(self, max_device_number):
        self.max_device_number = max_device_number
        self.usb_devices = []
        self.add_device()
        # for usb_device in self.usb_devices:
        # usb_device.item_display()
        if len(self.usb_devices) == 0:
            Log.print('No USB Serial devices detected.')

    ## Check if phone device is connected ##
    def connected_phone_device(self):
        for usb_device in self.usb_devices:
            if usb_device.is_phone:
                return True
        return False

    ## Verify USB device ##
    def is_usb_device(self, device, path=None):
        if 'ID_VENDOR' not in device.properties:
            return False
        if path is not None:
            if device.properties['DEVPATH'].find(path) == -1:
                return False
            for usb_device in self.usb_devices:
                if path.find(usb_device.devpath) >= 0:
                    return False
        return True

    ## Add USB device ##
    def add_device(self, path=None):
        self.context = pyudev.Context()
        for device in self.context.list_devices(subsystem='tty'):
            if self.is_usb_device(device, path):
                usb_device = UsbDevice(
                    device.device_node, device.properties['DEVPATH'], device.properties['ID_SERIAL_SHORT'], device.properties['ID_VENDOR'])
                self.set_devnum(usb_device)
                self.usb_devices.append(usb_device)
                # usb_device.item_display()
                if "SAMSUNG" in usb_device.vendor_name:
                    usb_device.set_phone()
                    Log.print(f'phone is {usb_device.comPort}')
                elif path is not None:
                    return usb_device.comPort
        return None

    ## Remove USB device ##
    def remove_device(self, path):
        path = path.partition('/tty')
        for usb_device in self.usb_devices:
            if path[0].find(usb_device.devpath) >= 0:
                self.usb_devices.remove(usb_device)
                return usb_device.comPort
        return None

    ## Find USB device ##
    def find_device(self, path):
        result = ""
        path = path.partition('/tty')
        for usb_device in self.usb_devices:
            if path[0].find(usb_device.devpath) >= 0:
                return usb_device
        return None

    ## Set device number ##
    def set_devnum(self, new_device):
        num = list(range(self.max_device_number))
        for usb_device in self.usb_devices:
            if usb_device.vendor_name == new_device.vendor_name:
                num.remove(usb_device.devnum)
        # Log.print('set devnum : %d - %s' %(num[0], new_device.comPort))
        new_device.set_devnum(num[0])

    ## Get USB device list ##
    def get_list(self):
        return self.usb_devices

    ## Reset USB device ##
    def reset_device(self, comPort):
        Log.print('manage reset usb device :' + comPort)
        for usb_device in self.usb_devices:
            if usb_device.comPort == comPort:
                Log.print('find usb device :' + comPort)
                usb_device.reset_device()
                break

## USB device class ##
class UsbDevice:
    ## Init class ##
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
        self.is_phone = False
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
    ## USB reset ##
    def reset_device(self):
        USBDEVFS_RESET = 21780
        try:
            f = open(self.usbpath, 'w', os.O_WRONLY)
            fcntl.ioctl(f, USBDEVFS_RESET, 0)
            Log.print('Successfully reset %s : %s' % (self.usbpath, self.comPort))
        except Exception as ex:
            Log.print('Failed to reset device! Error: %s' % ex)

    ## Set device bumber ##
    def set_devnum(self, devnum):
        self.devnum = devnum

    ## Set device as phone ##
    def set_phone(self):
        self.is_phone = True

    ## Display device information ##
    def item_display(self):
        Log.print('comPort = ' + self.comPort)
        Log.print('devpath = ' + self.devpath)
        Log.print('serial = ' + self.serial)
        Log.print('vendor_name = ' + self.vendor_name)
        Log.print('usbpath = ' + self.usbpath)
        Log.print('devnum = ', self.devnum)

# def main():
#    test = Usb_manager(10)

# if __name__ == "__main__":
#    main()
