from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class TempWindow(QDialog):

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
            'temperature.ui', 'thermometer_medium.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    def post_setup_window(self):
        # variables
        self.level = 0
        self.is_slider_pressed = False
        # device specific handler
        self.common_window.add_pipe_event_handler(self.event_handler)
        self.common_window.add_initial_value_handler(self.update_temparature_sensor)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.init_input_button()
        self.init_slider()

    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.horizontalSliderTemp = common_window.horizontalSliderTemp
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
        self.horizontalSliderTemp.setStyleSheet(Utils.get_ui_style_slider("COMMON"))

    def valueChanged(self):
        if self.is_slider_pressed:
            self.doubleSpinBoxInput.setValue(self.horizontalSliderTemp.value()/100)
            return
        if not self.is_slider_pressed:
            level = self.horizontalSliderTemp.value()/100
            # print(f'valueChanged : old ({self.level}), new ({level})')
            if self.level != level:
                self.update_temparature_sensor()

    def sliderPressed(self):
        self.is_slider_pressed = True

    def sliderReleased(self):
        self.is_slider_pressed = False
        level = self.horizontalSliderTemp.value()/100
        if self.level != level:
            self.update_temparature_sensor()

    def input_click(self):
        level = self.doubleSpinBoxInput.value()
        self.update_temparature_sensor(level)

    def set_temparature_level(self, level=None):
        if level is not None:
            self.level = level
        else:
            self.level = self.horizontalSliderTemp.value()/100
        self.level = max(min(self.level, TEMPERATURE_MAX_VAL), TEMPERATURE_MIN_VAL)

    def update_ui(self):
        self.horizontalSliderTemp.setValue(int(self.level*100))
        self.doubleSpinBoxInput.setValue(self.level)

    def update_temparature_sensor(self, level=None, need_command=True):
        self.set_temparature_level(level)
        self.update_ui()
        self.set_state()
        if need_command:
            TempCommand.set_temp(self.device_info.device_num, self.level)
            self.textBrowserLog.append(
                f'[Send] {self.level}{TEMPERATURE_UNIT}')

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

    def event_handler(self, event):
        if 'temp' in event:
            level = event.split(":")[1]
            self.update_temparature_sensor(int(level)/100, False)

    def eventFilter(self, obj, event):
        if obj is self.doubleSpinBoxInput and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.input_click()
                return True
        return super().eventFilter(obj, event)

    def autotest_event_handler(self, used_device):
        self.pushButtonInput.setEnabled(not used_device)
        self.horizontalSliderTemp.setEnabled(not used_device)
