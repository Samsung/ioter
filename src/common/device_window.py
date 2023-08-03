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
# File : device_window.py
# Description: Get device window by device type

from common.device_command import *
from common.common_window import CommonWindow
from common.test_window import TestWindow
from things.light import LightWindow
from things.doorlock import DoorlockWindow
from things.contact import ContactWindow
from things.doorlock import DoorlockWindow
from things.temperature import TempWindow
from things.humidity import HumidWindow
from things.lightsensor import LightsensorWindow
from things.occupancy import OccupancyWindow
from things.windowcovering import WindowcoveringWindow
from things.plugin_onoff import OnoffPlugin
from things.speaker import SpeakerWindow

## Get device window by device type ##
def get_device_window_by_device_type(device_type, device_info, use_test_window, window_manager):
    window_class = CommonWindow if not use_test_window else TestWindow
    window = {
        LIGHTBULB_DEVICE_TYPE: lambda device_info: LightWindow(device_info, window_class, window_manager),
        DOORLOCK_DEVICE_TYPE: lambda device_info: DoorlockWindow(device_info, window_class, window_manager),
        CONTACTSENSOR_DEVICE_TYPE: lambda device_info: ContactWindow(device_info, window_class, window_manager),
        TEMPERATURE_DEVICE_TYPE: lambda device_info: TempWindow(device_info, window_class, window_manager),
        HUMIDITY_DEVICE_TYPE: lambda device_info: HumidWindow(device_info, window_class, window_manager),
        LIGHTSENSOR_DEVICE_TYPE: lambda device_info: LightsensorWindow(device_info, window_class, window_manager),
        OCCUPANCY_DEVICE_TYPE: lambda device_info: OccupancyWindow(device_info, window_class, window_manager),
        WINDOWCOVERING_DEVICE_TYPE: lambda device_info: WindowcoveringWindow(
            device_info, window_class, window_manager),
        ONOFFPLUGIN_DEVICE_TYPE: lambda device_info: OnoffPlugin(
            device_info, window_class, window_manager),
        SPEAKER_DEVICE_TYPE: lambda device_info: SpeakerWindow(device_info, window_class, window_manager)
    }
    return window.get(device_type, None)(device_info)
