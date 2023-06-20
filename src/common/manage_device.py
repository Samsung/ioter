###########################################################################
#
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
# File : manage_device.py
# Description: Manage device properties and informations

from common.device_command import *
from common.log import Log
from common.manage_usb import UsbManager


'''
device number 
'''
global max_device_number
max_device_number = 10

## Main device manager class ##
class DeviceManager():
    ## Init class ##
    def __init__(self):
        self.max_device_number = max_device_number
        self.device_number = list(range(max_device_number))
        self.all_device_dict = dict()
        self.device_info_dict = dict()
        self.usb_manager = UsbManager(max_device_number)
        for usb_device in self.usb_manager.get_list():
            if not usb_device.is_phone:
                self.all_device_dict[usb_device.comPort] = -1

    ## Set used device information ##
    def set_used_device(self, comPort, device_info):
        if comPort in self.all_device_dict:
            deviceNum = self.device_number[0]
            self.all_device_dict[comPort] = deviceNum
            self.device_info_dict[deviceNum] = device_info
            self.device_number.remove(deviceNum)
            return self.all_device_dict[comPort]
        else:
            return None

    ## Set unused device information ##
    def set_unused_device(self, comPort):
        if comPort in self.all_device_dict:
            deviceNum = self.all_device_dict[comPort]
            if deviceNum != -1:
                del (self.device_info_dict[deviceNum])
                self.device_number.append(deviceNum)
                self.device_number.sort()
                self.all_device_dict[comPort] = -1
                return True
        return False

    ## Get list of used devices ##
    def get_used_devices(self):
        device_info_list = []
        for device_info in self.device_info_dict.values():
            device_info_list.append(device_info)
        return device_info_list  # return device_info list

    ## Get list of unused comPorts ##
    def get_unused_devices(self):
        unused_device_list = []
        all_device_list = list(self.all_device_dict.keys())
        for device in all_device_list:
            if self.all_device_dict[device] == -1:
                unused_device_list.append(device)
        unused_device_list.sort()
        return unused_device_list  # return comPort list

    ## Add USB device in deivce list ##
    def add_usb_device(self, path):
        comPort = self.usb_manager.add_device(path)
        if (comPort is not None) and (comPort not in self.all_device_dict):
            self.all_device_dict[comPort] = -1
#            Log.print('add device list')
            return comPort
        return None

    ## Remove USB device from deivce list ##
    def remove_usb_device(self, path):
        comPort = self.usb_manager.remove_device(path)
        if (comPort is not None) and (comPort in self.all_device_dict):
            self.set_unused_device(comPort)
            del (self.all_device_dict[comPort])
#            Log.print('remove device list')
        return comPort

    ## Get device number ##
    def get_device_number(self):
        return self.device_number

    ## Get device vendor ##
    def get_device_vendor(self, comPort):
        usb_devices = self.usb_manager.get_list()
        for usb_device in usb_devices:
            if usb_device.comPort == comPort:
                return usb_device.vendor_name

    ## Get device information by device number ##
    def get_device_info_by_device_num(self, device_number):
        return self.device_info_dict[device_number]

    ## Reset device ##
    def reset_device(self, comPort):
        Log.print('manage reset device')
        self.usb_manager.reset_device(comPort)


## Device information class ##
class DeviceInfo():

    VID = 4321 #0x10E1
    PID = {
        LIGHTBULB_DEVICE_ID: 4103,
        DOORLOCK_DEVICE_ID: 4098,
        CONTACTSENSOR_DEVICE_ID: 4112,
        TEMPERATURE_DEVICE_ID: 4099,
        HUMIDITY_DEVICE_ID: 4117,
        LIGHTSENSOR_DEVICE_ID: 4113,
        OCCUPANCY_DEVICE_ID: 4114,
        WINDOWCOVERING_DEVICE_ID: 4101,
        ONOFFPLUGIN_DEVICE_ID: 4106,
    }

    ## Init class ##
    def __init__(self, device_num, discriminator, thread_type, com_port, debug_level, ioter_name, deviceManager, device_id=0, auto=None):
        self.device_num = device_num
        self.discriminator = discriminator
        self.thread_type = thread_type
        self.com_port = com_port
        self.debug_level = debug_level
        self.ioter_name = ioter_name
        self.device_id = device_id
        self.thread_setting_file = 'undefined'
        self.commissioning_complete = False
        self.set_vid_pid(self.device_id)
        self.deviceManager = deviceManager
        self.auto = auto

    ## Set VID and PID ##
    def set_vid_pid(self, device_id):
        self.vid = self.VID
        self.pid = self.PID.get(device_id, 4105)
        Log.print(f'vid {self.vid}, pid {self.pid}')

    ## Set commissioning state ##
    def set_commissioning_state(self, state):
        self.commissioning_complete = state

    ## Get commissioning state ##
    def get_commissioning_state(self):
        return self.commissioning_complete

    ## Get device number ##
    def get_device_num(self):
        return self.device_num

    ## Get discriminator ##
    def get_discriminator(self):
        return self.discriminator

    ## Get thread type ##
    def get_thread_type(self):
        return self.thread_type

    ## Get com port ##
    def get_com_port(self):
        return self.com_port

    ## Get debug level ##
    def get_debug_level(self):
        return self.debug_level

    ## Get device id ##
    def get_device_id(self):
        return self.device_id

    ## Get ioter name ##
    def get_ioter_name(self):
        return self.ioter_name

    ## Get thread setting file ##
    def get_thread_setting_file(self):
        return self.thread_setting_file

    ## Set thread setting file ##
    def set_thread_setting_file(self, thread_setting_file):
        self.thread_setting_file = thread_setting_file

    ## Get auto status ##
    def get_auto(self):
        return self.auto
