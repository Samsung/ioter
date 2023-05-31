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
# File : light.py
# Description:
# Create and handles light bulb device type.

from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


SLIDER_DIM = "1"
SLIDER_COLOR = "2"

EVENT_TOGGLE = 1
EVENT_DIMMING = 2
EVENT_COLOR = 3
EVENT_SPINBOX_DIMMING = 4
EVENT_SPINBOX_COLOR = 5

## Light bulb device class ##
class LightWindow(QDialog):

    toggle_text = {
        True: 'Turn on',
        False: 'Turn off',
    }
    log_text = {
        EVENT_TOGGLE: 'Light',
        EVENT_DIMMING: 'Dimming',
        EVENT_COLOR: 'Color',
        EVENT_SPINBOX_DIMMING: 'Dimming',
        EVENT_SPINBOX_COLOR: 'Color'
    }
    toggle_icon = {
        True: 'lightbulb_on.png',
        False: 'lightbulb_off.png',
    }

    ## Initialise light bulb window and device info ##
    def __init__(self, device_info, window_class, window_manager):
        super().__init__()

        self.device_info = device_info

        self.pre_setup_window(window_class, window_manager)
        self.post_setup_window()

    ## Deinitialise light bulb window ##
    def __del__(self):
        del (self.common_window)

    ## Get light bulb window ##
    def get_window(self):
        return self.common_window

    ## UI setup for light bulb window ##
    def pre_setup_window(self, window_class, window_manager):
        self.common_window = window_class(
            'light.ui', 'lightbulb_off.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    ## Event handlers registration for light bulb window ##
    def post_setup_window(self):
        # variables
        self.is_slider_pressed = False
        self.state = False
        self.dimming_level = LIGHTBULB_DIM_DEFAULT
        self.color_level = LIGHTBULB_COLOR_TEMP_DEFAULT
        self.toggle_update_from_remote = False
        # device specific handler
        self.common_window.init_toggle_button()
        self.common_window.add_toggle_button_handler(self.toggle_handler)
        self.common_window.add_pipe_event_handler(self.event_handler)
        self.common_window.add_initial_value_handler(self.send_command)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.init_dim_slider()
        self.init_colortemp_slider()
        self.update_ui()

    ## Get UI component from Common window ##
    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.horizontalSliderDimming = common_window.horizontalSliderDimming
        self.pushButtonStatus = common_window.pushButtonStatus
        self.spinboxDimming = common_window.spinboxDimming
        self.textBrowserLog = common_window.textBrowserLog
        self.horizontalSliderColorTemp = common_window.horizontalSliderColorTemp
        self.spinboxColorTemp = common_window.spinboxColorTemp
        self.labelStatePicture = common_window.labelDevicePicture
        self.stackedWidget = common_window.stackedWidget

    ## Initialise UI Slider for dimming functionality##
    def init_dim_slider(self):
        self.horizontalSliderDimming.setRange(
            LIGHTBULB_DIM_MIN_VAL, LIGHTBULB_DIM_MAX_VAL)
        self.spinboxDimming.setRange(
            LIGHTBULB_DIM_MIN_VAL, LIGHTBULB_DIM_MAX_VAL)
        self.horizontalSliderDimming.setSingleStep(
            self.common_window.get_slider_single_step(LIGHTBULB_DIM_MIN_VAL, LIGHTBULB_DIM_MAX_VAL))
        self.spinboxDimming.setSingleStep(
            self.common_window.get_slider_single_step(LIGHTBULB_DIM_MIN_VAL, LIGHTBULB_DIM_MAX_VAL))
        self.horizontalSliderDimming.setValue(self.dimming_level)
        self.spinboxDimming.setValue(self.dimming_level)
        self.horizontalSliderDimming.sliderReleased.connect(
            lambda: self.sliderReleased(SLIDER_DIM))
        self.horizontalSliderDimming.valueChanged.connect(
            lambda: self.valueChanged(SLIDER_DIM))
        self.horizontalSliderDimming.sliderPressed.connect(
            self.sliderPressed)
        self.horizontalSliderDimming.setStyleSheet(
            Utils.get_ui_style_slider("DIMMING"))
        self.spinboxDimming.installEventFilter(self)

    ## Initialise UI Slider for color functionality##
    def init_colortemp_slider(self):
        self.horizontalSliderColorTemp.setRange(
            LIGHTBULB_COLOR_TEMP_MIN_VAL, LIGHTBULB_COLOR_TEMP_MAX_VAL)
        self.spinboxColorTemp.setRange(
            LIGHTBULB_COLOR_TEMP_MIN_VAL, LIGHTBULB_COLOR_TEMP_MAX_VAL)
        self.horizontalSliderColorTemp.setSingleStep(
            self.common_window.get_slider_single_step(LIGHTBULB_COLOR_TEMP_MIN_VAL, LIGHTBULB_COLOR_TEMP_MAX_VAL))
        self.spinboxColorTemp.setSingleStep(
            self.common_window.get_slider_single_step(LIGHTBULB_COLOR_TEMP_MIN_VAL, LIGHTBULB_COLOR_TEMP_MAX_VAL))
        self.horizontalSliderColorTemp.setValue(self.color_level)
        self.spinboxColorTemp.setValue(self.color_level)
        self.horizontalSliderColorTemp.sliderReleased.connect(
            lambda: self.sliderReleased(SLIDER_COLOR))
        self.horizontalSliderColorTemp.valueChanged.connect(
            lambda: self.valueChanged(SLIDER_COLOR))
        self.horizontalSliderColorTemp.sliderPressed.connect(
            self.sliderPressed)
        self.horizontalSliderColorTemp.setStyleSheet(
            Utils.get_ui_style_slider("COLORTEMP"))
        self.spinboxColorTemp.installEventFilter(self)

    ## Handle slider events for color and dimming ##
    def valueChanged(self, slider_id="0"):
        if self.is_slider_pressed and slider_id == SLIDER_DIM:
            self.spinboxDimming.setValue(self.horizontalSliderDimming.value())
            return
        elif self.is_slider_pressed and slider_id == SLIDER_COLOR:
            self.spinboxColorTemp.setValue(
                self.horizontalSliderColorTemp.value())
            return
        if slider_id == SLIDER_DIM:
            level = self.horizontalSliderDimming.value()
            # print(f'valueChanged dim: old ({self.dimming_level}) new({level})')
            if self.dimming_level != level:
                self.update_light(EVENT_DIMMING)
        elif slider_id == SLIDER_COLOR:
            level = self.horizontalSliderColorTemp.value()
            # print(f'valueChanged col: old ({self.color_level}), new ({level})')
            if self.color_level != level:
                self.update_light(EVENT_COLOR)

    ## Set slider state to pressed ##
    def sliderPressed(self):
        self.is_slider_pressed = True

    ## Set slider state to unpressed ##
    def sliderReleased(self, slider_id="0"):
        self.is_slider_pressed = False
        if slider_id == SLIDER_DIM:
            self.update_light(EVENT_DIMMING)
        elif slider_id == SLIDER_COLOR:
            self.update_light(EVENT_COLOR)

    ## Light bulb toggle event handler ##
    @pyqtSlot(bool)
    def toggle_handler(self, state):
        """
        light toggle button handler
        """
        # print(f'toggle_handler old ({self.state}), new ({state})')
        self.state = state
        if self.toggle_update_from_remote:
            self.toggle_update_from_remote = False
        else:
            self.update_light(EVENT_TOGGLE)


    ## Update light bulb window UI based on state/level ##
    def update_ui(self):
        # toggle
        self.pushButtonStatus.setStyleSheet(
            Utils.get_ui_style_toggle_btn(self.state))
        self.pushButtonStatus.setText(self.toggle_text.get(not self.state))
        # Dimming
        self.horizontalSliderDimming.setValue(self.dimming_level)
        self.spinboxDimming.setValue(self.dimming_level)
        # ColorTemp
        self.horizontalSliderColorTemp.setValue(self.color_level)
        self.spinboxColorTemp.setValue(self.color_level)
        # icon
        self.labelStatePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path(self.toggle_icon.get(self.state)), 70, 70))
        QApplication.processEvents()
        self.stackedWidget.update()

    ## Send command to light bulb device ##
    def send_command(self, event_type=EVENT_TOGGLE):
        if event_type is EVENT_TOGGLE:
            LightCommand.onOff(self.device_info.device_num, self.state)
            self.textBrowserLog.append(
                f'[Send] {self.toggle_text.get(self.state)}')
        elif event_type is EVENT_DIMMING or event_type is EVENT_SPINBOX_DIMMING:
            LightCommand.dimming(
                self.device_info.device_num, self.dimming_level)
            self.textBrowserLog.append(
                f'[Send] {self.dimming_level}{LIGHTBULB_DIM_UNIT}')
        elif event_type is EVENT_COLOR or event_type is EVENT_SPINBOX_COLOR:
            LightCommand.colortemp(
                self.device_info.device_num, self.color_level)
            self.textBrowserLog.append(
                f'[Send] {self.color_level}{LIGHTBULB_COLOR_TEMP_UNIT}')

    ## Update light bulb UI and device based on state/level ##
    def update_light(self, event_type, value=None, need_command=True):
        # set value
        if event_type is EVENT_TOGGLE:
            if value is not None and bool(value) != self.state:
                self.textBrowserLog.append(
                    f'[Recv] {self.log_text.get(event_type)} {self.toggle_text.get(bool(value))}')
                self.toggle_update_from_remote = True
                self.pushButtonStatus.toggle()
        elif event_type is EVENT_DIMMING:
            if value is not None and value != self.dimming_level:
                self.textBrowserLog.append(
                    f'[Recv] {self.log_text.get(event_type)} {round(value/LIGHTBULB_DIM_ST_CONVERT*100)}{LIGHTBULB_DIM_UNIT}')
            self.dimming_level = round(
                value/LIGHTBULB_DIM_ST_CONVERT*100) if value else self.horizontalSliderDimming.value()
        elif event_type is EVENT_COLOR:
            if value is not None and value != self.color_level:
                self.textBrowserLog.append(
                    f'[Recv] {self.log_text.get(event_type)} {int(round(1000000/value, 0)) if value else self.color_level}{LIGHTBULB_COLOR_TEMP_UNIT}')
            # We have to convert color level
            self.color_level = int(
                round(1000000/value, 0)) if value else self.horizontalSliderColorTemp.value()
        elif event_type is EVENT_SPINBOX_DIMMING:
            if value is not None and value != self.dimming_level:
                self.textBrowserLog.append(
                    f'[Recv] {self.log_text.get(event_type)} {round(value/LIGHTBULB_DIM_ST_CONVERT*100)}{LIGHTBULB_DIM_UNIT}')
            self.dimming_level = self.spinboxDimming.value()
        elif event_type is EVENT_SPINBOX_COLOR:
            if value is not None and value != self.color_level:
                self.textBrowserLog.append(
                    f'[Recv] {self.log_text.get(event_type)} {int(round(1000000/value, 0)) if value else self.color_level}{LIGHTBULB_COLOR_TEMP_UNIT}')
            self.color_level = self.spinboxColorTemp.value()
        else:
            return

        # ui update
        self.update_ui()

        # send command
        if need_command:
            self.send_command(event_type)

    ## pipeThread event handler ##
    def event_handler(self, event):
        event_type = None
        try:
            if 'onoff' in event:
                event_type = EVENT_TOGGLE
            elif 'level' in event:
                event_type = EVENT_DIMMING
            elif 'colortemp' in event:
                event_type = EVENT_COLOR
        except (IndexError, ValueError):
            self.textBrowserLog.append(
                'Error: Invalid event format - ' + event)
        if event_type:
            value = event.split(":")[1]
            self.update_light(event_type, int(value), False)

    ## UI event handler ##
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and (obj is self.spinboxDimming or obj is self.spinboxColorTemp):
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.update_light(
                    EVENT_SPINBOX_DIMMING if obj is self.spinboxDimming else EVENT_SPINBOX_COLOR)
                return True
        return super().eventFilter(obj, event)

    ## Autotest event handler ##
    def autotest_event_handler(self, used_device):
        self.horizontalSliderColorTemp.setEnabled(not used_device)
        self.horizontalSliderDimming.setEnabled(not used_device)
        self.pushButtonStatus.setEnabled(not used_device)

    ## Read and update the light bulb state based on value ##
    def setLightOnOff(self, value):
        state = self.pushButtonStatus.isChecked()
        if (value == "On" and not state) or (value == "Off" and state):
            self.pushButtonStatus.toggle()

    ## Get light bulb state ##
    def getLightOnOff(self):
        return "On" if self.pushButtonStatus.isChecked() else "Off"

    ## Set light bulb dimming level ##
    def setLevelControl(self, value):
        self.horizontalSliderDimming.setValue(int(value))

    ## Get light bulb dimming level ##
    def getLevelControl(self):
        return self.horizontalSliderDimming.value()

    ## Set light bulb color level ##
    def setColorControl(self, value):
        self.horizontalSliderColorTemp.setValue(int(value))

    ## Get light bulb color level ##
    def getColorControl(self):
        return self.horizontalSliderColorTemp.value()

    ## Read and update the light bulb power state based on value ##
    def setPowerOnOff(self, value):
        powerState = self.common_window.pushButtonDevicePower.isChecked()
        if (value == "On" and not powerState) or (value == "Off" and powerState):
            self.common_window.pushButtonDevicePower.toggle()

    ## Get light bulb power state ##
    def getPowerOnOff(self):
        return "On" if self.common_window.pushButtonDevicePower.isChecked() else "Off"

    ## Get light bulb supported commands ##
    def _return_command(self, value=None):
        command0 = {
            "Name": "Power On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setPowerOnOff,
            "Get_val": self.getPowerOnOff
        }
        command1 = {
            "Name": "Light On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setLightOnOff,
            "Get_val": self.getLightOnOff
        }
        command2 = {
            "Name": "Level Control %",
            "range": [LIGHTBULB_DIM_MIN_VAL, LIGHTBULB_DIM_MAX_VAL],
            "Set_val": self.setLevelControl,
            "Get_val": self.getLevelControl
        }
        command3 = {
            "Name": "Color Control K",
            "range": [LIGHTBULB_COLOR_TEMP_MIN_VAL, LIGHTBULB_COLOR_TEMP_MAX_VAL],
            "Set_val": self.setColorControl,
            "Get_val": self.getColorControl
        }
        return [command0, command1, command2, command3]
