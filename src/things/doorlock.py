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
# File : doorlock.py
# Description:
# Create and handles doorlock device type.

from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


LOCKED = 1
UNLOCKED = 2

## Doorlock device class ##
class DoorlockWindow(QDialog):

    toogle_text = {
        True: 'Lock',
        False: 'UnLock',
    }
    toggle_icon = {
        True: 'doorlock_on.png',
        False: 'doorlock_off.png',
    }

    ## Initialise doorlock window and device info ##
    def __init__(self, device_info, window_class, window_manager):
        super().__init__()

        self.device_info = device_info

        self.pre_setup_window(window_class, window_manager)
        self.post_setup_window()

    ## Deinitialise doorlock window ##
    def __del__(self):
        del self.common_window

    ## Get doorlock window ##
    def get_window(self):
        return self.common_window

    ## UI setup for doorlock window ##
    def pre_setup_window(self, window_class, window_manager):
        self.common_window = window_class(
            'doorlock.ui', 'doorlock_on.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    ## Event handlers registration for doorlock window ##
    def post_setup_window(self):
        # variables
        self.state = False
        self.toggle_update_from_remote = False
        # device specific handler
        self.common_window.init_toggle_button()
        self.common_window.add_toggle_button_handler(self.toggle_handler)
        self.common_window.add_pipe_event_handler(self.event_handler)
        self.common_window.add_initial_value_handler(
            self.send_doorlock_command)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.update_ui()

    ## Get UI component from common window ##
    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.pushButtonStatus = common_window.pushButtonStatus
        self.textBrowserLog = common_window.textBrowserLog
        self.labelStatePicture = common_window.labelDevicePicture

    ## Doorlock toggle event handler ##
    @pyqtSlot(bool)
    def toggle_handler(self, state):
        self.state = state
        self.update_ui()
        if self.toggle_update_from_remote:
            self.toggle_update_from_remote = False
        else:
            self.send_doorlock_command()

    ## Update doorlock window UI based on event ##
    def update_ui(self):
        self.pushButtonStatus.setStyleSheet(
            Utils.get_ui_style_toggle_btn(not self.state))
        self.pushButtonStatus.setText(self.toogle_text.get(not self.state))
        self.labelStatePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path(self.toggle_icon.get(self.state)), 70, 70))

    ## Send command to doorlock device ##
    def send_doorlock_command(self):
        DoorlockCommand.lockUnlock(self.device_info.device_num, self.state)
        self.textBrowserLog.append(
            f'[Send] {self.toogle_text.get(self.state)}')

    ## Verify the doorlock state for UI update ##
    def is_need_toggle(self, lock_state):
        if lock_state is LOCKED and not self.state:
            return True
        elif lock_state is UNLOCKED and self.state:
            return True
        else:
            return False

    ## Update doorlock window UI based on event ##
    def update_doorlock(self, lock_state):
        if self.is_need_toggle(lock_state):
            self.textBrowserLog.append(
                f'[Recv] {self.toogle_text.get(self.state)}')
            self.toggle_update_from_remote = True
            self.pushButtonStatus.toggle()

    ## pipeThread event handler ##
    def event_handler(self, event):
        if 'lock' in event:
            lock_state = event.split(":")[1]
            self.update_doorlock(int(lock_state))

    ## Autotest event handler ##
    def autotest_event_handler(self, used_device):
        self.pushButtonStatus.setEnabled(not used_device)

    ## Read and update the door lock state based on value ##
    def setDoorLockCmd(self, value):
        state = self.pushButtonStatus.isChecked()
        if (value == "Lock" and not state) or (value == "UnLock" and state):
            self.pushButtonStatus.toggle()

    ## Get door lock state ##
    def getDoorLockState(self):
        return self.toogle_text.get(self.pushButtonStatus.isChecked())

    ## Read and update the door lock power state based on value ##
    def setPowerOnOff(self, value):
        powerState = self.common_window.pushButtonDevicePower.isChecked()
        if (value == "On" and not powerState) or (value == "Off" and powerState):
            self.common_window.pushButtonDevicePower.toggle()

    ## Get door lock power state ##
    def getPowerOnOff(self):
        return "On" if self.common_window.pushButtonDevicePower.isChecked() else "Off"

    ## Get door lock supported commands ##
    def _return_command(self, value=None):
        command0 = {
            "Name": "Power On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setPowerOnOff,
            "Get_val": self.getPowerOnOff
        }
        command1 = {
            "Name": "Lock/UnLock",
            "val": ['Lock', 'UnLock'],
            "Set_val": self.setDoorLockCmd,
            "Get_val": self.getDoorLockState
        }
        return [command0, command1]
