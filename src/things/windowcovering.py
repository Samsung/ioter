from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

WC_MOVE_DOWN = -1
WC_MOVE_UP = 1
WC_INIT_LEVEL = 50


class WindowcoveringWindow(QDialog):

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
            'windowcovering.ui', 'windowcovering_8.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    def post_setup_window(self):
        # variables
        self.currentlevel = WC_INIT_LEVEL
        self.targetlevel = WC_INIT_LEVEL
        self.is_slider_pressed = False
        self.target_update_from_remote = False
        # device specific handler
        self.common_window.add_pipe_event_handler(self.event_handler)
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

    def init_open_button(self):
        self.openButton.setCheckable(True)
        self.openButton.setStyleSheet(
            Utils.get_ui_style_toggle_btn(True))
        self.openButton.clicked.connect(self.open_click)

    def init_close_button(self):
        self.closeButton.setCheckable(True)
        self.closeButton.setStyleSheet(
            Utils.get_ui_style_toggle_btn(True))
        self.closeButton.clicked.connect(self.close_click)

    def init_pause_button(self):
        self.pauseButton.setCheckable(True)
        self.pauseButton.setStyleSheet(
            Utils.get_ui_style_toggle_btn(True))
        self.pauseButton.clicked.connect(self.pause_click)

    def set_direction(self):
        if self.targetlevel >= self.currentlevel:
            self.direction = WC_MOVE_UP
        elif self.targetlevel < self.currentlevel:
            self.direction = WC_MOVE_DOWN

    def init_slider(self):
        self.horizontalSliderWindow.setRange(WINDOWCOVERING_MIN_VAL, WINDOWCOVERING_MAX_VAL)
        self.horizontalSliderWindow.setSingleStep(1)
        self.horizontalSliderWindow.setValue(WC_INIT_LEVEL)
        self.horizontalSliderWindow.sliderPressed.connect(
            self.slider_pressed)
        self.horizontalSliderWindow.sliderReleased.connect(
            self.slider_released)
        self.horizontalSliderWindow.valueChanged.connect(
            self.value_changed)
        self.labelSliderPercent.setText(f'{WC_INIT_LEVEL}{WINDOWCOVERING_UNIT}')

    def to_target(self):
        self.horizontalSliderWindow.setValue(self.targetlevel)
        self.labelSliderPercent.setText(str(self.targetlevel)+'%')
        if self.targetlevel != self.currentlevel:
            self.send_target_value()
            self.set_direction()
            self.timer.start(50)

    def value_changed(self):
        if not self.is_slider_pressed:
            self.timer.stop()
            level = self.horizontalSliderWindow.value()
            if level != self.targetlevel and level != self.currentlevel:
                self.targetlevel = level
            print(
                f'value_changed : target ({self.targetlevel}), current ({self.currentlevel})')
            self.to_target()

    def slider_pressed(self):
        self.timer.stop()
        self.is_slider_pressed = True

    def slider_released(self):
        self.is_slider_pressed = False
        self.timer.stop()
        self.targetlevel = self.horizontalSliderWindow.value()
        if self.targetlevel != self.currentlevel:
            self.to_target()

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

    def send_current_value(self):
        # pos = 10000 - (self.currentlevel * 100)
        WindowCoveringCommand.set_current_postion(
            self.device_info.device_num, self.currentlevel)
        self.textBrowserLog.append(
            f'[Send current] {self.currentlevel}{WINDOWCOVERING_UNIT}')

        """
        implement open/close/pause button
        """

    def open_click(self):
        self.timer.stop()
        self.targetlevel = WINDOWCOVERING_MAX_VAL
        self.to_target()

    def close_click(self):
        self.timer.stop()
        self.targetlevel = WINDOWCOVERING_MIN_VAL
        self.to_target()

    def pause_click(self):
        self.targetlevel = self.currentlevel
        self.set_state()

    def update_current_value(self):
        #self.currentlevel = self.horizontalCurrentSlider.value()
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
        if 'Matter-Onboarding is completed' in event:
            self.textBrowserLog.append(
                f'[Set to default position] {self.currentlevel}{WINDOWCOVERING_UNIT}')
            self.send_current_value()

    def autotest_event_handler(self, used_device):
        self.openButton.setEnabled(not used_device)
        self.closeButton.setEnabled(not used_device)
        self.pauseButton.setEnabled(not used_device)
        self.horizontalSliderWindow.setEnabled(not used_device)
