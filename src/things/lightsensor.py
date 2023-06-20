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
# File : lightsensor.py
# Description:
# Create and handles light sensor device type.

import math

from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

## Light sensor device class ##
class LightsensorWindow(QDialog):

    ## Initialise light sensor window and device info ##
    def __init__(self, device_info, window_class, window_manager):
        super().__init__()

        self.device_info = device_info

        self.pre_setup_window(window_class, window_manager)
        self.post_setup_window()

    ## Deinitialise light sensor window ##
    def __del__(self):
        del self.common_window

    ## Get light sensor window ##
    def get_window(self):
        return self.common_window

    ## UI setup for light sensor window ##
    def pre_setup_window(self, window_class, window_manager):
        self.common_window = window_class(
            'lightsensor.ui', 'lightsensor_low.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    ## Event handlers registration for light sensor window ##
    def post_setup_window(self):
        # variables
        self.measured_value = MEASURED_VALUE_MIN
        self.is_slider_pressed = False
        # device specific handler
        self.common_window.add_initial_value_handler(self.send_command)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.init_spinbox()
        self.init_slider()
        self.update_ui()

    ## Get UI component from common window ##
    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.horizontalSliderLightsensor = common_window.horizontalSliderLightsensor
        self.labelLightsensorLux = common_window.labelLightsensorLux
        self.spinBoxInput = common_window.spinBoxInput
        self.textBrowserLog = common_window.textBrowserLog
        self.labelStatePicture = common_window.labelDevicePicture

    ## Initialise UI input button ##
    def init_spinbox(self):
        self.spinBoxInput.installEventFilter(self)

    ## Initialise UI slider ##
    def init_slider(self):
        self.horizontalSliderLightsensor.setRange(
            MEASURED_VALUE_MIN, MEASURED_VALUE_MAX)
        self.horizontalSliderLightsensor.setSingleStep(
            self.common_window.get_slider_single_step(MEASURED_VALUE_MIN, MEASURED_VALUE_MAX))
        self.horizontalSliderLightsensor.setValue(self.measured_value)
        self.horizontalSliderLightsensor.sliderPressed.connect(
            self.sliderPressed)
        self.horizontalSliderLightsensor.sliderReleased.connect(
            self.sliderReleased)
        self.horizontalSliderLightsensor.valueChanged.connect(
            self.sliderValueChanged)
        self.horizontalSliderLightsensor.setStyleSheet(
            Utils.get_ui_style_slider("COMMON"))

    ## Update light sensor icon image based on level ##
    def set_state(self):
        if Utils.toIlluminance(self.measured_value) >= LIGHTSENSOR_BRIGHTNESS_LEVEL[1]:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('lightsensor_high.png'), 70, 70))
        elif LIGHTSENSOR_BRIGHTNESS_LEVEL[0] <= Utils.toIlluminance(self.measured_value) < LIGHTSENSOR_BRIGHTNESS_LEVEL[1]:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('lightsensor_medium.png'), 70, 70))
        else:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('lightsensor_low.png'), 70, 70))


    ## Handle slider events ##
    def sliderValueChanged(self):
        if self.is_slider_pressed:
            self.spinBoxInput.setValue(Utils.toIlluminance(
                self.horizontalSliderLightsensor.value()))
            return
        else:
            measured_value = self.horizontalSliderLightsensor.value()
            if self.measured_value != measured_value:
                self.update_light_sensor(measured_value)

    ## Set slider state to pressed ##
    def sliderPressed(self):
        self.is_slider_pressed = True

    ## Set slider state to unpressed ##
    def sliderReleased(self):
        self.is_slider_pressed = False
        measured_value = self.horizontalSliderLightsensor.value()
        if self.measured_value != measured_value:
            self.update_light_sensor(measured_value)

    ## Read and update input value ##
    def input_click(self):
        measured_value = Utils.findMeasuredValue(self.spinBoxInput.value())
        self.update_light_sensor(measured_value)

    ## Update light sensor window UI based on level ##
    def update_ui(self):
        self.spinBoxInput.setValue(Utils.toIlluminance(self.measured_value))
        self.horizontalSliderLightsensor.setValue(self.measured_value)

    ## Send command to light sensor device ##
    def send_command(self):
        LightsensorCommand.set_lightsensor(
            self.device_info.device_num, self.measured_value)
        self.get_window().appendTextBrowserLog(f'[Send] {self.spinBoxInput.value()}{LIGHTSENSOR_UNIT}')

    ## Update light sensor UI and device based on level ##
    def update_light_sensor(self, measured_value):
        self.measured_value = measured_value
        self.update_ui()
        self.set_state()
        self.send_command()

    ## UI event handler ##
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.spinBoxInput:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.input_click()
                return True
        return super().eventFilter(obj, event)

    ## Autotest event handler ##
    def autotest_event_handler(self, used_device):
        self.horizontalSliderLightsensor.setEnabled(not used_device)

    ## Read and update the light sensor state based on value ##
    def setLightSensorValue(self, value):
        measured_value = Utils.findMeasuredValue(int(value))
        self.horizontalSliderLightsensor.setValue(measured_value)

    ## Get light sensor state ##
    def getLightSensorValue(self):
        return self.spinBoxInput.value()

    ## Read and update the light sensor power state based on value ##
    def setPowerOnOff(self, value):
        powerState = self.common_window.pushButtonDevicePower.isChecked()
        if (value == "On" and not powerState) or (value == "Off" and powerState):
            self.common_window.pushButtonDevicePower.toggle()

    ## Get light sensor power state ##
    def getPowerOnOff(self):
        return "On" if self.common_window.pushButtonDevicePower.isChecked() else "Off"

    ## Get light sensor supported commands ##
    def _return_command(self, value=None):
        command0 = {
            "Name": "Power On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setPowerOnOff,
            "Get_val": self.getPowerOnOff
        }
        command1 = {
            "Name": "Level Control lux",
            "range": [LIGHTSENSOR_MIN_VAL, LIGHTSENSOR_MAX_VAL],
            "Set_val": self.setLightSensorValue,
            "Get_val": self.getLightSensorValue
        }
        return [command0, command1]
