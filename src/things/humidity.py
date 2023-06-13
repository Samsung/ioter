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
# File : humidity.py
# Description:
# Create and handles humidity device type.

from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

## Humidity device class ##
class HumidWindow(QDialog):

    ## Initialise humidity window and device info ##
    def __init__(self, device_info, window_class, window_manager):
        super().__init__()

        self.device_info = device_info

        self.pre_setup_window(window_class, window_manager)
        self.post_setup_window()

    ## Deinitialise humidity window ##
    def __del__(self):
        del self.common_window

    ## Get humidity window ##
    def get_window(self):
        return self.common_window

    ## UI setup for humidity window ##
    def pre_setup_window(self, window_class, window_manager):
        self.common_window = window_class(
            'humidity.ui', 'humidity_0.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    ## Event handlers registration for humidity window ##
    def post_setup_window(self):
        # variables
        self.level = HUMIDITY_MIN_VAL
        self.is_slider_pressed = False
        # device specific handler
        self.common_window.add_initial_value_handler(
            self.update_humidity_sensor)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.init_input_button()
        self.init_slider()

    ## Get UI component from common window ##
    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.horizontalSliderHumid = common_window.horizontalSliderHumid
        self.labelSliderPercent = common_window.labelSliderPercent
        self.doubleSpinBoxInput = common_window.doubleSpinBoxInput
        self.pushButtonInput = common_window.pushButtonInput
        self.textBrowserLog = common_window.textBrowserLog
        self.labelStatePicture = common_window.labelDevicePicture

    ## Initialise UI Input Button ##
    def init_input_button(self):
        self.pushButtonInput.setCheckable(True)
        self.pushButtonInput.setStyleSheet(
            Utils.get_ui_style_toggle_btn(True))
        self.pushButtonInput.clicked.connect(self.input_click)
        self.doubleSpinBoxInput.installEventFilter(self)

    ## Initialise UI Slider ##
    def init_slider(self):
        self.horizontalSliderHumid.setRange(HUMIDITY_MIN_VAL, HUMIDITY_MAX_VAL)
        self.horizontalSliderHumid.setSingleStep(
            self.common_window.get_slider_single_step(HUMIDITY_MIN_VAL, HUMIDITY_MAX_VAL))
        self.horizontalSliderHumid.setValue(self.level)
        self.horizontalSliderHumid.sliderPressed.connect(
            self.sliderPressed)
        self.horizontalSliderHumid.sliderReleased.connect(
            self.sliderReleased)
        self.horizontalSliderHumid.valueChanged.connect(
            self.valueChanged)
        self.horizontalSliderHumid.setStyleSheet(
            Utils.get_ui_style_slider("COMMON"))

    ## Handle slider events ##
    def valueChanged(self):
        if self.is_slider_pressed:
            self.doubleSpinBoxInput.setValue(
                self.horizontalSliderHumid.value()/100)
            return
        if not self.is_slider_pressed:
            level = self.horizontalSliderHumid.value()/100
            # print(f'valueChanged : old ({self.level}), new ({level})')
            if self.level != level:
                self.update_humidity_sensor(level)

    ## Set slider state to pressed ##
    def sliderPressed(self):
        self.is_slider_pressed = True

    ## Set slider state to unpressed ##
    def sliderReleased(self):
        self.is_slider_pressed = False
        level = self.horizontalSliderHumid.value()/100
        if self.level != level:
            self.update_humidity_sensor(level)

    ## Read and update input value ##
    def input_click(self):
        level = self.doubleSpinBoxInput.value()
        self.update_humidity_sensor(level)

    ## Set humidity level ##
    def set_humidity_level(self, level):
        self.level = max(min(level, HUMIDITY_MAX_VAL), HUMIDITY_MIN_VAL)

    ## Update humidity window UI based on level ##
    def update_ui(self):
        self.horizontalSliderHumid.setValue(int(self.level*100))
        self.doubleSpinBoxInput.setValue(self.level)

    ## Update humidity window UI and device based on level ##
    def update_humidity_sensor(self, level = 0):
        self.set_humidity_level(level)
        self.update_ui()
        self.set_state()
        HumidCommand.set_humid(self.device_info.device_num, self.level)
        self.textBrowserLog.append(
            f'[Send] {self.level}{HUMIDITY_UNIT}')

    ## Update humidity icon image based on level ##
    def set_state(self):
        if self.level >= 90:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('humidity_100.png'), 70, 70))
        elif self.level >= 50:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('humidity_66.png'), 70, 70))
        elif self.level >= 10:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('humidity_33.png'), 70, 70))
        else:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('humidity_0.png'), 70, 70))

    ## UI event handler ##
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.doubleSpinBoxInput:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.input_click()
                return True
        return super().eventFilter(obj, event)

    ## Autotest event handler ##
    def autotest_event_handler(self, used_device):
        self.pushButtonInput.setEnabled(not used_device)
        self.horizontalSliderHumid.setEnabled(not used_device)

    ## Read and update the humidity state based on value ##
    def setHumidityValue(self, value):
        self.horizontalSliderHumid.setValue(int(value)*100)

    ## Get humidity state ##
    def getHumidityValue(self):
        return int(self.horizontalSliderHumid.value()/100)

    ## Read and update the humidity sensor power state based on value ##
    def setPowerOnOff(self, value):
        powerState = self.common_window.pushButtonDevicePower.isChecked()
        if (value == "On" and not powerState) or (value == "Off" and powerState):
            self.common_window.pushButtonDevicePower.toggle()

    ## Get humidity power state ##
    def getPowerOnOff(self):
        return "On" if self.common_window.pushButtonDevicePower.isChecked() else "Off"

    ## Get humidity supported commands ##
    def _return_command(self, value=None):
        command0 = {
            "Name": "Power On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setPowerOnOff,
            "Get_val": self.getPowerOnOff
        }
        command1 = {
            "Name": "Level Control %",
            "range": [HUMIDITY_MIN_VAL, int(HUMIDITY_MAX_VAL/100)],
            "Set_val": self.setHumidityValue,
            "Get_val": self.getHumidityValue
        }
        return [command0, command1]
