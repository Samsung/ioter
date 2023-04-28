from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class LightsensorWindow(QDialog):

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
            'lightsensor.ui', 'lightsensor_low.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    def post_setup_window(self):
        # variables
        self.set_light_sensor_level(LIGHTSENSOR_MIN_VAL)
        self.is_slider_pressed = False
        # device specific handler
        self.common_window.add_pipe_event_handler(self.event_handler)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.init_input_button()
        self.init_slider()
        self.update_ui()

    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.horizontalSliderLightsensor = common_window.horizontalSliderLightsensor
        self.labelLightsensorLux = common_window.labelLightsensorLux
        self.spinBoxInput = common_window.spinBoxInput
        self.pushButtonInput = common_window.pushButtonInput
        self.textBrowserLog = common_window.textBrowserLog
        self.labelStatePicture = common_window.labelDevicePicture

    def init_input_button(self):
        self.pushButtonInput.setCheckable(True)
        self.pushButtonInput.setStyleSheet(
            Utils.get_ui_style_toggle_btn(True))
        self.pushButtonInput.clicked.connect(self.input_click)
        self.spinBoxInput.installEventFilter(self)

    def init_slider(self):
        self.horizontalSliderLightsensor.setRange(LIGHTSENSOR_MIN_VAL, LIGHTSENSOR_MAX_VAL)
        self.horizontalSliderLightsensor.setSingleStep(
            self.common_window.get_slider_single_step(LIGHTSENSOR_MIN_VAL, LIGHTSENSOR_MAX_VAL))
        self.horizontalSliderLightsensor.setValue(self.level)
        self.horizontalSliderLightsensor.sliderPressed.connect(
            self.sliderPressed)
        self.horizontalSliderLightsensor.sliderReleased.connect(
            self.sliderReleased)
        self.horizontalSliderLightsensor.valueChanged.connect(
            self.valueChanged)
        self.horizontalSliderLightsensor.setStyleSheet(Utils.get_ui_style_slider("COMMON"))
        
    def set_state(self):
        if self.level >= 50000 :
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path('lightsensor_high.png'), 70, 70))
        elif 10000 <= self.level < 50000 :
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path('lightsensor_medium.png'), 70, 70))
        else:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path('lightsensor_low.png'), 70, 70))

    def valueChanged(self):
        if self.is_slider_pressed:
            self.spinBoxInput.setValue(self.horizontalSliderLightsensor.value())
            return
        if not self.is_slider_pressed:
            level = self.horizontalSliderLightsensor.value()
            # print(f"valueChanged: old ({self.level}), new ({level})")
            if self.level != level:
                self.update_light_sensor()

    def sliderPressed(self):
        self.is_slider_pressed = True

    def sliderReleased(self):
        self.is_slider_pressed = False
        level = self.horizontalSliderLightsensor.value()
        if self.level != level:
            self.update_light_sensor()

    def input_click(self):
        level = self.spinBoxInput.value()
        self.update_light_sensor(level)

    def set_light_sensor_level(self, level=None):
        self.level = level or self.horizontalSliderLightsensor.value()
        self.level = max(min(self.level, LIGHTSENSOR_MAX_VAL), LIGHTSENSOR_MIN_VAL)

    def update_ui(self):
        self.spinBoxInput.setValue(self.level)
        self.horizontalSliderLightsensor.setValue(self.level)

    def send_command(self):
        LightsensorCommand.set_lightsensor(
            self.device_info.device_num, self.level)
        self.textBrowserLog.append(f'[Send] {self.level}{LIGHTSENSOR_UNIT}')

    def update_light_sensor(self, level=None, need_command=True):
        self.set_light_sensor_level(level)
        self.update_ui()
        self.set_state()
        if need_command:
            self.send_command()

    def eventFilter(self, obj, event):
        if obj is self.spinBoxInput and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.input_click()
                return True
        return super().eventFilter(obj, event)

    def event_handler(self, event):
        if 'illum' in event:
            self.update_light_sensor(int(event.split(":")[1]), False)

    def autotest_event_handler(self, used_device):
        self.pushButtonInput.setEnabled(not used_device)
        self.horizontalSliderLightsensor.setEnabled(not used_device)
