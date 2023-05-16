from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class OnoffPlugin(QDialog):

    toggle_text = {
        True: 'Turn on',
        False: 'Turn off',
    }
    toggle_icon = {
        True: 'switch_on.png',
        False: 'switch_off.png',
    }

    def __init__(self, device_info, window_class, window_manager):
        super().__init__()

        self.device_info = device_info

        self.pre_setup_window(window_class, window_manager)
        self.post_setup_window()

    def __del__(self):
        del self.common_window

    def get_window(self):
        return self.common_window

    def pre_setup_window(self, window_class, window_manager):
        self.common_window = window_class(
            'onoffplugin.ui', 'switch_off.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

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

    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.pushButtonStatus = common_window.pushButtonStatus
        self.textBrowserLog = common_window.textBrowserLog
        self.labelStatePicture = common_window.labelDevicePicture

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

    def update_ui(self):
        self.pushButtonStatus.setStyleSheet(
            Utils.get_ui_style_toggle_btn(self.state))
        self.pushButtonStatus.setText(self.toggle_text.get(not self.state))
        self.labelStatePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path(self.toggle_icon.get(self.state)), 70, 70))

    def send_plugin_command(self):
        OnOffPluginCommand.onOff(self.device_info.device_num, self.state)
        self.textBrowserLog.append(
            f'[Send] {self.toggle_text.get(self.state)}')

    def update_plugin(self, onoff):
        if onoff != self.state:
            self.textBrowserLog.append(f'[Recv] {self.toggle_text.get(onoff)}')
            self.toggle_update_from_remote = True
            self.pushButtonStatus.toggle()

    def event_handler(self, event):
        if 'onoff' in event:
            state = event.split(":")[1]
            self.update_plugin(bool(int(state)))

    def autotest_event_handler(self, used_device):
        self.pushButtonStatus.setEnabled(not used_device)
