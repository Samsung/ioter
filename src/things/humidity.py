from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class HumidWindow(QDialog):

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
            'humidity.ui', 'humidity_0.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    def post_setup_window(self):
        # variables
        self.level = HUMIDITY_MIN_VAL
        self.is_slider_pressed = False
        # device specific handler
        self.common_window.add_pipe_event_handler(self.event_handler)
        self.common_window.add_initial_value_handler(self.update_humidity_sensor)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.init_input_button()
        self.init_slider()

    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.horizontalSliderHumid = common_window.horizontalSliderHumid
        self.labelSliderPercent = common_window.labelSliderPercent
        self.doubleSpinBoxInput = common_window.doubleSpinBoxInput
        self.pushButtonInput = common_window.pushButtonInput
        self.textBrowserLog = common_window.textBrowserLog
        self.labelStatePicture = common_window.labelDevicePicture

    def init_input_button(self):
        self.pushButtonInput.setCheckable(True)
        self.pushButtonInput.setStyleSheet(
            Utils.get_ui_style_toggle_btn(True))
        self.pushButtonInput.clicked.connect(self.input_click)
        self.doubleSpinBoxInput.installEventFilter(self)

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
        self.horizontalSliderHumid.setStyleSheet(Utils.get_ui_style_slider("COMMON"))

    def valueChanged(self):
        if self.is_slider_pressed:
            self.doubleSpinBoxInput.setValue(self.horizontalSliderHumid.value()/100)
            return
        if not self.is_slider_pressed:
            level = self.horizontalSliderHumid.value()/100
            # print(f'valueChanged : old ({self.level}), new ({level})')
            if self.level != level:
                self.update_humidity_sensor()

    def sliderPressed(self):
        self.is_slider_pressed = True

    def sliderReleased(self):
        self.is_slider_pressed = False
        level = self.horizontalSliderHumid.value()/100
        if self.level != level:
            self.update_humidity_sensor()

    def input_click(self):
        level = self.doubleSpinBoxInput.value()
        self.update_humidity_sensor(level)

    def set_humidity_level(self, level=None):
        self.level = level or self.horizontalSliderHumid.value()/100
        self.level = max(min(self.level, HUMIDITY_MAX_VAL), HUMIDITY_MIN_VAL)

    def update_ui(self):
        self.horizontalSliderHumid.setValue(int(self.level*100))
        self.doubleSpinBoxInput.setValue(self.level)

    def update_humidity_sensor(self, level=None, need_command=True):
        self.set_humidity_level(level)
        self.update_ui()
        self.set_state()
        if need_command:
            HumidCommand.set_humid(self.device_info.device_num, self.level)
            self.textBrowserLog.append(
                f'[Send] {self.level}{HUMIDITY_UNIT}')

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

    def event_handler(self, event):
        if 'humid' in event:
            level = event.split(":")[1]
            self.update_humidity_sensor(int(level)/100, False)

    def eventFilter(self, obj, event):
        if obj is self.doubleSpinBoxInput and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.input_click()
                return True
        return super().eventFilter(obj, event)

    def autotest_event_handler(self, used_device):
        self.pushButtonInput.setEnabled(not used_device)
        self.horizontalSliderHumid.setEnabled(not used_device)
