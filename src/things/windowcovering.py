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
# File : windowcovering.py
# Description:
# Create and handles window covering device type.

from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

WC_MOVE_DOWN = -1
WC_MOVE_UP = 1
WC_INIT_LEVEL = 50

## Window covering device class ##
class WindowcoveringWindow(QDialog):

    ## Initialise window covering UI and device info ##
    def __init__(self, device_info, window_class, window_manager):
        super().__init__()

        self.device_info = device_info

        self.pre_setup_window(window_class, window_manager)
        self.post_setup_window()

    ## Deinitialise window covering UI ##
    def __del__(self):
        del self.common_window

    ## Get UI window for window covering ##
    def get_window(self):
        return self.common_window

    ## UI setup for window covering ##
    def pre_setup_window(self, window_class, window_manager):
        self.common_window = window_class(
            'windowcovering.ui', 'windowcovering_8.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    ## Event handlers registration for window covering ##
    def post_setup_window(self):
        # variables
        self.currentlevel = WC_INIT_LEVEL
        self.targetlevel = WC_INIT_LEVEL
        self.is_slider_pressed = False
        self.target_update_from_remote = False
        # device specific handler
        self.common_window.add_pipe_event_handler(self.event_handler)
        self.common_window.add_initial_value_handler(self.send_current_value)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.set_state()
        self.init_open_button()
        self.init_close_button()
        self.init_pause_button()
        self.init_slider()

        self.timer = QTimer(self)  # Create a timer object
        # Connect the timer signal to its slot
        self.timer.timeout.connect(self.update_current_value)

    ## Get UI component from common window ##
    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.labelDevicePicture = common_window.labelDevicePicture
        self.horizontalSliderWindow = common_window.horizontalSliderWindow
        self.labelCoveringState = common_window.labelDevicePicture
        self.labelSliderPercent = common_window.labelSliderPercent
        self.openButton = common_window.openButton
        self.closeButton = common_window.closeButton
        self.pauseButton = common_window.pauseButton
        self.textBrowserLog = common_window.textBrowserLog

    ## Update window covering icon image based on level ##
    def set_state(self):
        if self.currentlevel == 100:
            self.labelCoveringState.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('windowcovering_0.png'), 70, 70))
        elif self.currentlevel >= 89:
            self.labelCoveringState.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('windowcovering_1.png'), 70, 70))
        elif self.currentlevel >= 76:
            self.labelCoveringState.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('windowcovering_2.png'), 70, 70))
        elif self.currentlevel >= 63:
            self.labelCoveringState.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('windowcovering_3.png'), 70, 70))
        elif self.currentlevel >= 50:
            self.labelCoveringState.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('windowcovering_4.png'), 70, 70))
        elif self.currentlevel >= 37:
            self.labelCoveringState.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('windowcovering_5.png'), 70, 70))
        elif self.currentlevel >= 24:
            self.labelCoveringState.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('windowcovering_6.png'), 70, 70))
        elif self.currentlevel >= 11:
            self.labelCoveringState.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('windowcovering_7.png'), 70, 70))
        else:
            self.labelCoveringState.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('windowcovering_8.png'), 70, 70))


    ## Initialise open button for window covering UI ##
    def init_open_button(self):
        self.openButton.setCheckable(True)
        self.openButton.setStyleSheet(
            Utils.get_ui_style_toggle_btn(True))
        self.openButton.clicked.connect(self.open_click)

    ## Initialise close button for window covering UI ##
    def init_close_button(self):
        self.closeButton.setCheckable(True)
        self.closeButton.setStyleSheet(
            Utils.get_ui_style_toggle_btn(True))
        self.closeButton.clicked.connect(self.close_click)


    ## Initialise pause button for window covering UI ##
    def init_pause_button(self):
        self.pauseButton.setCheckable(True)
        self.pauseButton.setStyleSheet(
            Utils.get_ui_style_toggle_btn(True))
        self.pauseButton.clicked.connect(self.pause_click)


    ## Set window cover direction based on current level ##
    def set_direction(self):
        if self.targetlevel >= self.currentlevel:
            self.direction = WC_MOVE_UP
        elif self.targetlevel < self.currentlevel:
            self.direction = WC_MOVE_DOWN

    ## Initialise UI slider ##
    def init_slider(self):
        self.horizontalSliderWindow.setRange(
            WINDOWCOVERING_MIN_VAL, WINDOWCOVERING_MAX_VAL)
        self.horizontalSliderWindow.setSingleStep(1)
        self.horizontalSliderWindow.setValue(WC_INIT_LEVEL)
        self.horizontalSliderWindow.sliderPressed.connect(
            self.slider_pressed)
        self.horizontalSliderWindow.sliderReleased.connect(
            self.slider_released)
        self.horizontalSliderWindow.valueChanged.connect(
            self.value_changed)
        self.labelSliderPercent.setText(
            f'{WC_INIT_LEVEL}{WINDOWCOVERING_UNIT}')
        self.horizontalSliderWindow.setStyleSheet(
            Utils.get_ui_style_slider("COMMON"))

    ## Set the window cover to target value ##
    def to_target(self):
        self.horizontalSliderWindow.setValue(self.targetlevel)
        self.labelSliderPercent.setText(str(self.targetlevel)+'%')
        if self.targetlevel != self.currentlevel:
            self.send_target_value()
            self.set_direction()
            self.timer.start(50)

    ## Handle slider events ##
    def value_changed(self):
        if not self.is_slider_pressed:
            self.timer.stop()
            level = self.horizontalSliderWindow.value()
            if level != self.targetlevel and level != self.currentlevel:
                self.targetlevel = level
            print(
                f'value_changed : target ({self.targetlevel}), current ({self.currentlevel})')
            self.to_target()

    ## Set slider state to pressed ##
    def slider_pressed(self):
        self.timer.stop()
        self.is_slider_pressed = True

    ## Set slider state to unpressed ##
    def slider_released(self):
        self.is_slider_pressed = False
        self.timer.stop()
        self.targetlevel = self.horizontalSliderWindow.value()
        if self.targetlevel != self.currentlevel:
            self.to_target()

    ## Send command to window cover device with target value ##
    def send_target_value(self):
        if self.target_update_from_remote:
            print("send_target_value : do not send")
            self.target_update_from_remote = False
            return
        # pos = 10000 - (self.targetlevel * 100)
        WindowCoveringCommand.set_target_position(
            self.device_info.device_num, self.targetlevel)
        self.textBrowserLog.append(
            f'[Send target] {self.targetlevel}{WINDOWCOVERING_UNIT}')

    ## Send command to window cover device with current value ##
    def send_current_value(self):
        # pos = 10000 - (self.currentlevel * 100)
        WindowCoveringCommand.set_current_postion(
            self.device_info.device_num, self.currentlevel)
        self.textBrowserLog.append(
            f'[Send current] {self.currentlevel}{WINDOWCOVERING_UNIT}')

    ## Handle opening of the window cover ##
    def open_click(self):
        self.timer.stop()
        self.targetlevel = WINDOWCOVERING_MAX_VAL
        self.to_target()

    ## Handle closing of the window cover ##
    def close_click(self):
        self.timer.stop()
        self.targetlevel = WINDOWCOVERING_MIN_VAL
        self.to_target()

    ## Handle pausing of the window cover ##
    def pause_click(self):
        self.targetlevel = self.currentlevel
        self.set_state()

    ## Update window cover position based on current level ##
    def update_current_value(self):
        # self.currentlevel = self.horizontalCurrentSlider.value()
        if self.direction is WC_MOVE_UP:
            self.currentlevel = min(self.currentlevel + 1, self.targetlevel)
        elif self.direction is WC_MOVE_DOWN:
            self.currentlevel = max(self.currentlevel - 1, self.targetlevel)
        self.set_state()
        if self.currentlevel == self.targetlevel:
            self.timer.stop()
            self.send_current_value()
            self.horizontalSliderWindow.setValue(self.targetlevel)
        elif (self.currentlevel % 10) == 0:  # ui update in units of 10
            self.send_current_value()

    ## pipeThread event handler ##
    def event_handler(self, event):
        # self.textBrowserLog.append(event)
        if 'go-to-percentage' in event:
            targetlevel = int((10000 - int(event.split(":")[1])) / 100)
            if self.targetlevel != targetlevel:
                self.target_update_from_remote = True
                self.targetlevel = targetlevel
                self.horizontalSliderWindow.setValue(self.targetlevel)
                self.labelSliderPercent.setText(f"{self.targetlevel}%")
                self.textBrowserLog.append(
                    f'[Recv target] {self.targetlevel}{WINDOWCOVERING_UNIT}')
                self.timer.stop()
                self.to_target()

    ## Autotest event handler ##
    def autotest_event_handler(self, used_device):
        self.openButton.setEnabled(not used_device)
        self.closeButton.setEnabled(not used_device)
        self.pauseButton.setEnabled(not used_device)
        self.horizontalSliderWindow.setEnabled(not used_device)

    ## Read and update the window cover position based on value ##
    def setWindowcoveringValue(self, value):
        self.horizontalSliderWindow.setValue(int(value))

    ## Get window cover position ##
    def getWindowcoveringValue(self):
        return self.horizontalSliderWindow.value()

    ## Read and update the window cover power state based on value ##
    def setPowerOnOff(self, value):
        powerState = self.common_window.pushButtonDevicePower.isChecked()
        if (value == "On" and not powerState) or (value == "Off" and powerState):
            self.common_window.pushButtonDevicePower.toggle()

    ## Get window cover power state ##
    def getPowerOnOff(self):
        return "On" if self.common_window.pushButtonDevicePower.isChecked() else "Off"

    ## Get window cover supported commands ##
    def _return_command(self, value=None):
        command0 = {
            "Name": "Power On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setPowerOnOff,
            "Get_val": self.getPowerOnOff
        }
        command1 = {
            "Name": "Level Control %",
            "range": [0, 100],
            "Set_val": self.setWindowcoveringValue,
            "Get_val": self.getWindowcoveringValue
        }
        return [command0, command1]
