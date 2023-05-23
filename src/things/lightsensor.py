import math
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
        self.set_light_sensor_measured_value(MEASURED_VALUE_MIN)
        self.is_slider_pressed = False
        # device specific handler
        self.common_window.add_pipe_event_handler(self.event_handler)
        self.common_window.add_initial_value_handler(self.send_command)
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
        self.horizontalSliderLightsensor.setRange(
            MEASURED_VALUE_MIN, MEASURED_VALUE_MAX)
        self.horizontalSliderLightsensor.setSingleStep(
            self.common_window.get_slider_single_step(MEASURED_VALUE_MIN, MEASURED_VALUE_MAX))
        self.horizontalSliderLightsensor.setValue(self.measured_value)
        self.horizontalSliderLightsensor.sliderPressed.connect(
            self.sliderPressed)
        self.horizontalSliderLightsensor.sliderReleased.connect(
            self.sliderReleased)
        self.horizontalSliderLightsensor.valueChanged.connect(
            self.sliderValueChanged)
        self.horizontalSliderLightsensor.setStyleSheet(
            Utils.get_ui_style_slider("COMMON"))

    def set_state(self):
        if self.toIlluminance(self.measured_value) >= 50000:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('lightsensor_high.png'), 70, 70))
        elif 10000 <= self.toIlluminance(self.measured_value) < 50000:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('lightsensor_medium.png'), 70, 70))
        else:
            self.labelStatePicture.setPixmap(Utils.get_icon_img(
                Utils.get_icon_path('lightsensor_low.png'), 70, 70))

    def sliderValueChanged(self):
        if self.is_slider_pressed:
            self.spinBoxInput.setValue(self.toIlluminance(
                self.horizontalSliderLightsensor.value()))
            return
        else:
            measured_value = self.horizontalSliderLightsensor.value()
            if self.measured_value != measured_value:
                self.set_light_sensor_measured_value(measured_value)
                self.update_light_sensor()

    def sliderPressed(self):
        self.is_slider_pressed = True

    def sliderReleased(self):
        self.is_slider_pressed = False
        measured_value = self.horizontalSliderLightsensor.value()
        if self.measured_value != measured_value:
            self.set_light_sensor_measured_value(measured_value)
            self.update_light_sensor()

    def input_click(self):
        self.set_light_sensor_measured_value(
            self.toMeasuredValue(self.spinBoxInput.value()))
        self.spinBoxInput.setValue(self.toIlluminance(self.measured_value))
        self.update_light_sensor(self.measured_value)

    def set_light_sensor_measured_value(self, measured_value):
        self.measured_value = measured_value
        if self.measured_value < LIGHTSENSOR_MIN_VAL:
            self.measured_value = LIGHTSENSOR_MIN_VAL
        elif self.measured_value > LIGHTSENSOR_MAX_VAL:
            self.measured_value = LIGHTSENSOR_MAX_VAL

    def update_ui(self):
        self.spinBoxInput.setValue(self.toIlluminance(self.measured_value))
        self.horizontalSliderLightsensor.setValue(self.measured_value)

    def send_command(self):
        LightsensorCommand.set_lightsensor(
            self.device_info.device_num, self.measured_value)
        self.textBrowserLog.append(f'[Send] {self.measured_value}')

    def update_light_sensor(self, need_command=True):
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
            self.update_light_sensor(False)

    def autotest_event_handler(self, used_device):
        self.pushButtonInput.setEnabled(not used_device)
        self.horizontalSliderLightsensor.setEnabled(not used_device)

    def toIlluminance(self, value):
        return int(pow(10, (value-1)/10000))

    def toMeasuredValue(self, illum):
        return round(10000*math.log(illum, 10)+1)

# auto test
    def setLightSensorValue(self, value):
        self.spinBoxInput.setValue(int(value))
        self.input_click()

    def getLightSensorValue(self):
        return self.spinBoxInput.value()

    def setPowerOnOff(self, value):
        powerState = self.common_window.pushButtonDevicePower.isChecked()
        if (value == "On" and not powerState) or (value == "Off" and powerState):
            self.common_window.pushButtonDevicePower.toggle()

    def getPowerOnOff(self):
        return "On" if self.common_window.pushButtonDevicePower.isChecked() else "Off"

    def _return_command(self, value=None):
        command0 = {
            "Name": "Power On/Off",
            "val": ['On', 'Off'],
            "Set_val": self.setPowerOnOff,
            "Get_val": self.getPowerOnOff
        }
        command1 = {
            "Name": "Level Control lux",
            "range": [LIGHTSENSOR_MIN_VAL, LIGHTSENSOR_MAX_VAL],
            "Set_val": self.setLightSensorValue,
            "Get_val": self.getLightSensorValue
        }
        return [command0, command1]
