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
# File : temperature.py
# Description:
# Create and handles temperature device type.

from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

## Temperature device class ##
class TempWindow(QDialog):

    ## Initialise temperature window and device info ##
    def __init__(self, device_info, window_class, window_manager):
        super().__init__()

        self.device_info = device_info

        self.pre_setup_window(window_class, window_manager)
        self.post_setup_window()

    ## Deinitialise temperature window ##
    def __del__(self):
        del self.common_window

    ## Get temperature window ##
    def get_window(self):
        return self.common_window

    ## UI setup for temperature window ##
    def pre_setup_window(self, window_class, window_manager):
        self.common_window = window_class(
            'temperature.ui', 'thermometer_medium.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    ## Event handlers registration for temperature window ##
    def post_setup_window(self):
        # variables
        self.level = 0
        self.is_slider_pressed = False
        # device specific handler
        self.common_window.add_initial_value_handler(
            self.update_temparature_sensor)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.init_spinbox()
        self.init_slider()

    ## Get UI component from common window ##
    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.horizontalSliderTemp = common_window.horizontalSliderTemp
        self.doubleSpinBoxInput = common_window.doubleSpinBoxInput
        self.textBrowserLog = common_window.textBrowserLog
        self.labelStatePicture = common_window.labelDevicePicture

    ## Initialise UI input button ##
    def init_spinbox(self):
        self.doubleSpinBoxInput.installEventFilter(self)

    ## Initialise UI slider ##
    def init_slider(self):
        self.horizontalSliderTemp.setRange(
            int(TEMPERATURE_MIN_VAL*100), int(TEMPERATURE_MAX_VAL*100))
        self.doubleSpinBoxInput.setDecimals(2)
        self.horizontalSliderTemp.setSingleStep(
            self.common_window.get_slider_single_step(TEMPERATURE_MIN_VAL, TEMPERATURE_MAX_VAL))
        self.horizontalSliderTemp.setValue(int(self.level*100))
        self.horizontalSliderTemp.sliderPressed.connect(
            self.sliderPressed)
        self.horizontalSliderTemp.sliderReleased.connect(
            self.sliderReleased)
        self.horizontalSliderTemp.valueChanged.connect(
            self.valueChanged)
        self.horizontalSliderTemp.setStyleSheet(
            Utils.get_ui_style_slider("COMMON"))

    ## Handle slider events ##
    def valueChanged(self):
        if self.is_slider_pressed:
            self.doubleSpinBoxInput.setValue(
                self.horizontalSliderTemp.value()/100)
            return
        if not self.is_slider_pressed:
            level = self.horizontalSliderTemp.value()/100
            if self.level != level:
                self.update_temparature_sensor(level)

    ## Set slider state to pressed ##
    def sliderPressed(self):
        self.is_slider_pressed = True

    ## Set slider state to unpressed ##
    def sliderReleased(self):
        self.is_slider_pressed = False
        level = self.horizontalSliderTemp.value()/100
        if self.level != level:
            self.update_temparature_sensor(level)

    ## Read and update input value ##
    def input_click(self):
        level = self.doubleSpinBoxInput.value()
        self.update_temparature_sensor(level)

    ## Set temperature level ##
    def set_temparature_level(self, level):
        self.level = max(min(level, TEMPERATURE_MAX_VAL),
                         TEMPERATURE_MIN_VAL)

    ## Update temperature window UI based on level ##
    def update_ui(self):
        self.horizontalSliderTemp.setValue(int(self.level*100))
        self.doubleSpinBoxInput.setValue(self.level)

    ## Update temperature UI and device based on level ##
    def update_temparature_sensor(self, level = 0):
        self.set_temparature_level(level)
        self.update_ui()
        self.set_state()
        TempCommand.set_temp(self.device_info.device_num, self.level)
        self.get_window().appendTextBrowserLog(
            f'[Send] {self.level}{TEMPERATURE_UNIT}')

    ## Update thermometer icon image based on level ##
    def set_state(self):
        if self.level > 100:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('thermometer_high.png'), 70, 70))
        elif self.level < 0:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('thermometer_low.png'), 70, 70))
        elif 0 <= self.level <= 100:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('thermometer_medium.png'), 70, 70))

    ## UI event handler ##
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.doubleSpinBoxInput:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.input_click()
                return True
        return super().eventFilter(obj, event)

    ## Autotest event handler ##
    def autotest_event_handler(self, used_device):
        self.horizontalSliderTemp.setEnabled(not used_device)

    ## Read and update the temperature based on value ##
    def setTemperatureValue(self, value):
        self.horizontalSliderTemp.setValue(int(float(value)*100))

    ## Get temperature ##
    def getTemperatureValue(self):
        return self.horizontalSliderTemp.value()/100

    ## Read and update the temperature sensor power state based on value ##
    def setPowerOnOff(self, value):
        powerState = self.common_window.pushButtonDevicePower.isChecked()
        if (value == "On" and not powerState) or (value == "Off" and powerState):
            self.common_window.pushButtonDevicePower.toggle()

    ## Get temperature power state ##
    def getPowerOnOff(self):
        return "On" if self.common_window.pushButtonDevicePower.isChecked() else "Off"

    ## Get temperature supported commands ##
    def _return_command(self, value=None):
        command0 = {
            "Name": "Power On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setPowerOnOff,
            "Get_val": self.getPowerOnOff
        }
        command1 = {
            "Name": "Level Control °C",
            "range": [TEMPERATURE_MIN_VAL, TEMPERATURE_MAX_VAL],
            "Set_val": self.setTemperatureValue,
            "Get_val": self.getTemperatureValue
        }
        return [command0, command1]
