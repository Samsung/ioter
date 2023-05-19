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
# File : plugin_onoff.py
# Description:
# Create and handles onoff plugin device type.

from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

## Onoff plugin device class ##
class OnoffPlugin(QDialog):

    toggle_text = {
        True: 'Turn on',
        False: 'Turn off',
    }
    toggle_icon = {
        True: 'switch_on.png',
        False: 'switch_off.png',
    }

    ## Initialise onoff plugin window and device info ##
    def __init__(self, device_info, window_class, window_manager):
        super().__init__()

        self.device_info = device_info

        self.pre_setup_window(window_class, window_manager)
        self.post_setup_window()

    ## Deinitialise onoff plugin window ##
    def __del__(self):
        del self.common_window

    ## Get onoff plugin window ##
    def get_window(self):
        return self.common_window

    ## UI setup for onoff plugin window ##
    def pre_setup_window(self, window_class, window_manager):
        self.common_window = window_class(
            'onoffplugin.ui', 'switch_off.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    ## Event handlers registration for onoff plugin window ##
    def post_setup_window(self):
        # variables
        self.state = False
        self.toggle_update_from_remote = False
        # device specific handler
        self.common_window.init_toggle_button()
        self.common_window.add_toggle_button_handler(self.toggle_handler)
        self.common_window.add_pipe_event_handler(self.event_handler)
        self.common_window.add_initial_value_handler(self.send_plugin_command)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.update_ui()

    ## Get UI component from common window ##
    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.pushButtonStatus = common_window.pushButtonStatus
        self.textBrowserLog = common_window.textBrowserLog
        self.labelStatePicture = common_window.labelDevicePicture

    ## Onoff plugin UI button event handler ##
    @pyqtSlot(bool)
    def toggle_handler(self, state):
        """
        on off plugin toggle button handler
        """
        # print(f'toggle_handler old ({self.state}), new ({state})')
        self.state = state
        self.update_ui()
        if self.toggle_update_from_remote:
            self.toggle_update_from_remote = False
        else:
            self.send_plugin_command()

    ## Update onoff plugin window UI based on state ##
    def update_ui(self):
        self.pushButtonStatus.setStyleSheet(
            Utils.get_ui_style_toggle_btn(self.state))
        self.pushButtonStatus.setText(self.toggle_text.get(not self.state))
        self.labelStatePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path(self.toggle_icon.get(self.state)), 70, 70))

    ## Send command to onoff plugin device ##
    def send_plugin_command(self):
        OnOffPluginCommand.onOff(self.device_info.device_num, self.state)
        self.textBrowserLog.append(
            f'[Send] {self.toggle_text.get(self.state)}')

    ## Update onoff plugin UI and device based on state ##
    def update_plugin(self, onoff):
        if onoff != self.state:
            self.textBrowserLog.append(f'[Recv] {self.toggle_text.get(onoff)}')
            self.toggle_update_from_remote = True
            self.pushButtonStatus.toggle()

    ## pipeThread event handler ##
    def event_handler(self, event):
        if 'onoff' in event:
            state = event.split(":")[1]
            self.update_plugin(bool(int(state)))

    ## Autotest event handler ##
    def autotest_event_handler(self, used_device):
        self.pushButtonStatus.setEnabled(not used_device)

    ## Read and update the onoff plugin state based on value ##
    def setPluginCmd(self, value):
        state = self.pushButtonStatus.isChecked()
        if (value == "On" and not state) or (value == "Off" and state):
            self.pushButtonStatus.toggle()

    ## Get onoff plugin state ##
    def getPluginState(self):
        return "On" if self.pushButtonStatus.isChecked() else "Off"

    ## Read and update the onoff plugin power state based on value ##
    def setPowerOnOff(self, value):
        powerState = self.common_window.pushButtonDevicePower.isChecked()
        if (value == "On" and not powerState) or (value == "Off" and powerState):
            self.common_window.pushButtonDevicePower.toggle()

    ## Get onoff plugin power state ##
    def getPowerOnOff(self):
        return "On" if self.common_window.pushButtonDevicePower.isChecked() else "Off"

    ## Get onoff plugin supported commands ##
    def _return_command(self, value=None):
        command0 = {
            "Name": "Power On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setPowerOnOff,
            "Get_val": self.getPowerOnOff
        }
        command1 = {
            "Name": "On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setPluginCmd,
            "Get_val": self.getPluginState
        }
        return [command0, command1]
