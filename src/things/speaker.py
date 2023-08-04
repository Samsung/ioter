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
# File : speaker.py
# Description:
# Create and handles speaker device type.

from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

EVENT_TOGGLE = 1
EVENT_VOLUME_CONTROL = 2

## Speaker device class ##
class SpeakerWindow(QDialog):

    toggle_text = {
        True: 'Unmute',
        False: 'Mute',
    }
    log_text = {
        EVENT_TOGGLE: 'Volume',
        EVENT_VOLUME_CONTROL: 'Volume',
    }
    toggle_icon = {
        True: 'audio_on.png',
        False: 'audio_off.png',
    }

    ## Initialise speaker window and device info ##
    def __init__(self, device_info, window_class, window_manager):
        super().__init__()
        self.device_info = device_info
        self.pre_setup_window(window_class, window_manager)
        self.post_setup_window()

    ## Deinitialise speaker window ##
    def __del__(self):
        del (self.common_window)

    ## Get speaker window ##
    def get_window(self):
        return self.common_window

    ## UI setup for speaker window ##
    def pre_setup_window(self, window_class, window_manager):
        self.common_window = window_class(
            'speaker.ui', 'audio_off.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    ## Event handlers registration for speaker window ##
    def post_setup_window(self):
        # variables
        self.is_slider_pressed = False
        self.state = False
        self.volume_level = SPEAKER_VOL_DEFAULT
        self.toggle_update_from_remote = False
        self.file_opened = False

        # device specific handler
        self.common_window.init_toggle_button()
        self.common_window.add_toggle_button_handler(self.toggle_handler)
        self.common_window.add_pipe_event_handler(self.event_handler)
        self.common_window.add_initial_value_handler(self.send_command)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.init_volume_slider()
        self.update_ui()

    ## Get UI component from Common window ##
    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.pushButtonDeviceMuteStatus = common_window.pushButtonStatus
        self.horizontalSliderVolumeControl = common_window.horizontalSliderVolumeControl
        self.textBrowserLog = common_window.textBrowserLog
        self.labelStatePicture = common_window.labelDevicePicture
        self.stackedWidget = common_window.stackedWidget
    
    ## Initialise UI Slider for volume functionality##
    def init_volume_slider(self):
        self.horizontalSliderVolumeControl.setRange(
            SPEAKER_VOL_MIN_VAL, SPEAKER_VOL_MAX_VAL)
        self.horizontalSliderVolumeControl.setSingleStep(
            self.common_window.get_slider_single_step(SPEAKER_VOL_MIN_VAL, SPEAKER_VOL_MAX_VAL)*10)
        self.horizontalSliderVolumeControl.setPageStep(
            self.common_window.get_slider_single_step(SPEAKER_VOL_MIN_VAL, SPEAKER_VOL_MAX_VAL)*10)
        self.horizontalSliderVolumeControl.setValue(self.volume_level)
        self.horizontalSliderVolumeControl.sliderReleased.connect(self.sliderReleased)
        self.horizontalSliderVolumeControl.valueChanged.connect(self.valueChanged)
        self.horizontalSliderVolumeControl.sliderPressed.connect(self.sliderPressed)
        self.horizontalSliderVolumeControl.setStyleSheet(
            Utils.get_ui_style_slider("COMMON"))        
        
    ## Handle slider events for Volume control ##
    def valueChanged(self):
        level = self.horizontalSliderVolumeControl.value()
        if self.volume_level != level:
            self.update_volume(EVENT_VOLUME_CONTROL)

    ## Set slider state to pressed ##
    def sliderPressed(self):
        self.is_slider_pressed = True

    ## Set slider state to unpressed ##
    def sliderReleased(self):
        self.is_slider_pressed = False
        self.update_volume(EVENT_VOLUME_CONTROL)

    ## Speaker Mute/Unmute toggle event handler ##
    @pyqtSlot(bool)
    def toggle_handler(self, state):
        """
        Speaker Mute/Unmute toggle button handler
        """
        self.state = state
        if self.toggle_update_from_remote:
            self.toggle_update_from_remote = False
        else:
            self.update_volume(EVENT_TOGGLE)


    ## Update speaker window UI based on state/level ##
    def update_ui(self):
        # toggle
        self.pushButtonDeviceMuteStatus.setStyleSheet(
            Utils.get_ui_style_toggle_btn(self.state))
        self.pushButtonDeviceMuteStatus.setText(self.toggle_text.get(not self.state))

        # Volume control
        self.horizontalSliderVolumeControl.setValue(self.volume_level)

        # icon
        self.labelStatePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path(self.toggle_icon.get(self.state)), 70, 70))
        QApplication.processEvents()
        self.stackedWidget.update()

    ## Send command to speaker device ##
    def send_command(self, event_type=EVENT_TOGGLE):
        if event_type is EVENT_TOGGLE:
            SpeakerCommand.onOff(self.device_info.device_num, self.state)
            self.get_window().appendTextBrowserLog(
                f'[Send] {self.toggle_text.get(self.state)}')
        elif event_type is EVENT_VOLUME_CONTROL:
            SpeakerCommand.set_volume(
                self.device_info.device_num, self.volume_level)
            self.get_window().appendTextBrowserLog(
                f'[Send] {self.volume_level}')

    ## Update speaker UI and device based on state/level ##
    def update_volume(self, event_type, value=None, need_command=True):
        # set value
        if event_type is EVENT_TOGGLE:
            if value is not None and bool(value) != self.state:
                self.get_window().appendTextBrowserLog(
                    f'[Recv] {self.log_text.get(event_type)} {self.toggle_text.get(bool(value))}')
                self.toggle_update_from_remote = True
                self.pushButtonDeviceMuteStatus.toggle()
        elif event_type is EVENT_VOLUME_CONTROL:
            if value is not None and value != self.volume_level:
                self.get_window().appendTextBrowserLog(
                    f'[Recv] {self.log_text.get(event_type)} {round(value/SPEAKER_VOL_ST_CONVERT*100)}')
            self.volume_level = round(
                value/SPEAKER_VOL_ST_CONVERT*100) if value else self.horizontalSliderVolumeControl.value()
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
                event_type = EVENT_VOLUME_CONTROL
        except (IndexError, ValueError):
            self.get_window().appendTextBrowserLog(
                'Error: Invalid event format - ' + event)
        if event_type:
            value = event.split(":")[1]
            self.update_volume(event_type, int(value), False)

    ## Autotest event handler ##
    def autotest_event_handler(self, used_device):
        self.horizontalSliderVolumeControl.setEnabled(not used_device)
        self.pushButtonDeviceMuteStatus.setEnabled(not used_device)

    ## Read and update the speaker state based on value ##
    def setVolumeMuteUnmute(self, value):
        state = self.pushButtonDeviceMuteStatus.isChecked()
        if (value == "Mute" and not state) or (value == "Unmute" and state):
            self.pushButtonDeviceMuteStatus.toggle()

    ## Get volume mute/unmute state ##
    def getVolumeMuteUnmute(self):
        return "Mute" if self.pushButtonDeviceMuteStatus.isChecked() else "Unmute"

    ## Set speaker dimming level ##
    def setLevelControl(self, value):
        self.horizontalSliderVolumeControl.setValue(int(value))

    ## Get speaker dimming level ##
    def getLevelControl(self):
        return self.horizontalSliderVolumeControl.value()

    ## Read and update the speaker power state based on value ##
    def setPowerOnOff(self, value):
        powerState = self.common_window.pushButtonDevicePower.isChecked()
        if (value == "On" and not powerState) or (value == "Off" and powerState):
            self.common_window.pushButtonDevicePower.toggle()

    ## Get speaker power state ##
    def getPowerOnOff(self):
        return "On" if self.common_window.pushButtonDevicePower.isChecked() else "Off"

    ## Get speaker supported commands ##
    def _return_command(self, value=None):
        command0 = {
            "Name": "Power On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setPowerOnOff,
            "Get_val": self.getPowerOnOff
        }
        command1 = {
            "Name": "Volume Mute/Unmute",
            "val": ['Unmute', 'Mute'],
            "Set_val": self.setVolumeMuteUnmute,
            "Get_val": self.getVolumeMuteUnmute
        }
        command2 = {
            "Name": "Volume Level Control",
            "range": [SPEAKER_VOL_MIN_VAL, SPEAKER_VOL_MAX_VAL],
            "Set_val": self.setLevelControl,
            "Get_val": self.getLevelControl
        }
        return [command0, command1, command2]
