from common.utils import Utils
from common.device_command import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


SLIDER_DIM = "1"
SLIDER_COLOR = "2"

EVENT_TOGGLE = 1
EVENT_DIMMING = 2
EVENT_COLOR = 3


class LightWindow(QDialog):

    toogle_text = {
        True: 'Turn on',
        False: 'Turn off',
    }
    log_text = {
        EVENT_TOGGLE: 'Light',
        EVENT_DIMMING: 'Dimming',
        EVENT_COLOR: 'Color'
    }
    toggle_icon = {
        True: 'lightbulb_on.png',
        False: 'lightbulb_off.png',
    }

    def __init__(self, device_info, window_class, window_manager):
        super().__init__()

        self.device_info = device_info

        self.pre_setup_window(window_class, window_manager)
        self.post_setup_window()

    def __del__(self):
        del (self.common_window)

    def get_window(self):
        return self.common_window

    def pre_setup_window(self, window_class, window_manager):
        self.common_window = window_class(
            'light.ui', 'lightbulb_off.png', self.device_info, self, window_manager)
        self.get_ui_component_from_common_window(self.common_window)

    def post_setup_window(self):
        # variables
        self.is_slider_pressed = False
        self.state = False
        self.dimming_level = LIGHTBULB_DIM_MIN_VAL
        self.color_level = LIGHTBULB_COLOR_TEMP_MIN_VAL
        self.toggle_update_from_remote = False
        # device specific handler
        self.common_window.init_toggle_button()
        self.common_window.add_toggle_button_handler(self.toggle_handler)
        self.common_window.add_pipe_event_handler(self.event_handler)
        self.common_window.add_autotest_event_handler(
            self.autotest_event_handler)
        self.init_dim_slider()
        self.init_colortemp_slider()

    def get_ui_component_from_common_window(self, common_window):
        # device specific ui component
        self.horizontalSliderDimming = common_window.horizontalSliderDimming
        self.pushButtonStatus = common_window.pushButtonStatus
        self.labelDimmingPercent = common_window.labelDimmingPercent
        self.textBrowserLog = common_window.textBrowserLog
        self.horizontalSliderColorTemp = common_window.horizontalSliderColorTemp
        self.labelColorTemp = common_window.labelColorTemp
        self.labelStatePicture = common_window.labelDevicePicture
        self.stackedWidget = common_window.stackedWidget

    def init_dim_slider(self):
        self.horizontalSliderDimming.setRange(
            LIGHTBULB_DIM_MIN_VAL, LIGHTBULB_DIM_MAX_VAL)
        self.horizontalSliderDimming.setSingleStep(
            self.common_window.get_slider_single_step(LIGHTBULB_DIM_MIN_VAL, LIGHTBULB_DIM_MAX_VAL))
        self.horizontalSliderDimming.setValue(self.dimming_level)
        self.horizontalSliderDimming.sliderReleased.connect(
            lambda: self.sliderReleased(SLIDER_DIM))
        self.horizontalSliderDimming.valueChanged.connect(
            lambda: self.valueChanged(SLIDER_DIM))
        self.horizontalSliderDimming.sliderPressed.connect(
            self.sliderPressed)
        onboarding_style_sheet = """
            QSlider::groove:horizontal {
            border: 1px solid #bbb;
            background: white;
            height: 7.5px;
            border-radius: 4px;
            }
            QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #eee, stop:1 #ccc);
            border: 1px solid #777;
            width: 13px;
            margin-top: -4px;
            margin-bottom: -4px;
            border-radius: 4px;
            }
            QSlider::handle:horizontal:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #fff, stop:1 #ddd);
            border: 1px solid #444;
            border-radius: 4px;
            }
        """
        self.horizontalSliderDimming.setStyleSheet(onboarding_style_sheet)

    def init_colortemp_slider(self):
        self.horizontalSliderColorTemp.setRange(
            LIGHTBULB_COLOR_TEMP_MIN_VAL, LIGHTBULB_COLOR_TEMP_MAX_VAL)
        self.horizontalSliderColorTemp.setSingleStep(
            self.common_window.get_slider_single_step(LIGHTBULB_COLOR_TEMP_MIN_VAL, LIGHTBULB_COLOR_TEMP_MAX_VAL))
        self.horizontalSliderColorTemp.setValue(self.color_level)
        self.horizontalSliderColorTemp.sliderReleased.connect(
            lambda: self.sliderReleased(SLIDER_COLOR))
        self.horizontalSliderColorTemp.valueChanged.connect(
            lambda: self.valueChanged(SLIDER_COLOR))
        self.horizontalSliderColorTemp.sliderPressed.connect(
            self.sliderPressed)
        onboarding_style_sheet = """
            QSlider::groove:horizontal {
            border: 1px solid #bbb;
            background: white;
            height: 7.5px;
            border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #eee, stop:1 #ccc);
            border: 1px solid #777;
            width: 13px;
            margin-top: -4px;
            margin-bottom: -4px;
            border-radius: 4px;
            }
            QSlider::handle:horizontal:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #fff, stop:1 #ddd);
            border: 1px solid #444;
            border-radius: 4px;
            }
        """
        self.horizontalSliderColorTemp.setStyleSheet(onboarding_style_sheet)

    def valueChanged(self, slider_id="0"):
        if self.is_slider_pressed:
            return
        if slider_id == SLIDER_DIM:
            level = self.horizontalSliderDimming.value()
            # print(f'valueChanged dim: old ({self.dimming_level}) new({level})')
            if self.dimming_level != level:
                self.update_light(EVENT_DIMMING)
        elif slider_id == SLIDER_COLOR:
            level = self.horizontalSliderColorTemp.value()
            # print(f'valueChanged col: old ({self.color_level}), new ({level})')
            if self.color_level != level:
                self.update_light(EVENT_COLOR)

    def sliderPressed(self):
        self.is_slider_pressed = True

    def sliderReleased(self, slider_id="0"):
        self.is_slider_pressed = False
        if slider_id == SLIDER_DIM:
            self.update_light(EVENT_DIMMING)
        elif slider_id == SLIDER_COLOR:
            self.update_light(EVENT_COLOR)

    @pyqtSlot(bool)
    def toggle_handler(self, state):
        """
        light toggle button handler
        """
        # print(f'toggle_handler old ({self.state}), new ({state})')
        self.state = state
        if self.toggle_update_from_remote:
            self.toggle_update_from_remote = False
        else:
            self.update_light(EVENT_TOGGLE)

    def update_ui(self):
        # toggle
        self.pushButtonStatus.setStyleSheet(
            Utils.get_ui_style_toggle_btn(self.state))
        self.pushButtonStatus.setText(self.toogle_text.get(self.state))
        # dimming slider
        self.horizontalSliderDimming.setValue(self.dimming_level)
                # rgb(58, 134, 255)
        onboarding_style_sheet = """
            QSlider::groove:horizontal {
            border: 1px solid #bbb;
            background: white;
            height: 7.5px;
            border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
            background: #3a86ff;
            border: 1px solid #777;
            height: 10px;
            border-radius: 4px;
            }
            QSlider::add-page:horizontal {
            background: #fff;
            border: 1px solid #777;
            height: 10px;
            border-radius: 4px;
            }
            QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #eee, stop:1 #ccc);
            border: 1px solid #777;
            width: 13px;
            margin-top: -4px;
            margin-bottom: -4px;
            border-radius: 4px;
            }
            QSlider::handle:horizontal:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #fff, stop:1 #ddd);
            border: 1px solid #444;
            border-radius: 4px;
            }
        """
        self.horizontalSliderDimming.setStyleSheet(onboarding_style_sheet)
        self.labelDimmingPercent.setText(
            f'{self.dimming_level}{LIGHTBULB_DIM_UNIT}')
        # colortemp slider
        # rgb(58, 134, 255)
        onboarding_style_sheet = """
            QSlider::groove:horizontal {
            border: 1px solid #bbb;
            background: white;
            height: 7.5px;
            border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
            background: qlineargradient(x1: 0, y1: 1, x2: 1, y2: 1,
                stop: 0 #a5c6fa, stop: 1 #3a86ff);
            border: 1px solid #777;
            height: 10px;
            border-radius: 4px;
            }
            QSlider::add-page:horizontal {
            background: #fff;
            border: 1px solid #777;
            height: 10px;
            border-radius: 4px;
            }
            QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #eee, stop:1 #ccc);
            border: 1px solid #777;
            width: 13px;
            margin-top: -4px;
            margin-bottom: -4px;
            border-radius: 4px;
            }
            QSlider::handle:horizontal:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #fff, stop:1 #ddd);
            border: 1px solid #444;
            border-radius: 4px;
            }
            QSlider::sub-page:horizontal:disabled {
            background: #bbb;
            border-color: #999;
            }
            QSlider::add-page:horizontal:disabled {
            background: #eee;
            border-color: #999;
            }
            QSlider::handle:horizontal:disabled {
            background: #eee;
            border: 1px solid #aaa;
            border-radius: 4px;
            }
        """
        self.horizontalSliderColorTemp.setStyleSheet(onboarding_style_sheet)
        self.horizontalSliderColorTemp.setValue(self.color_level)
        self.labelColorTemp.setText(
            f'{self.color_level}{LIGHTBULB_COLOR_TEMP_UNIT}')
        # icon
        self.labelStatePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path(self.toggle_icon.get(self.state)), 70, 70))
        QApplication.processEvents()
        self.stackedWidget.update()

    def send_command(self, event_type):
        if event_type is EVENT_TOGGLE:
            LightCommand.onOff(self.device_info.device_num, self.state)
            self.textBrowserLog.append(
                f'[Send] {self.toogle_text.get(self.state)}')
        elif event_type is EVENT_DIMMING:
            LightCommand.dimming(
                self.device_info.device_num, self.dimming_level)
            self.textBrowserLog.append(
                f'[Send] {self.dimming_level}{LIGHTBULB_DIM_UNIT}')
        elif event_type is EVENT_COLOR:
            LightCommand.colortemp(
                self.device_info.device_num, self.color_level)
            self.textBrowserLog.append(
                f'[Send] {self.color_level}{LIGHTBULB_COLOR_TEMP_UNIT}')

    def is_invalid_command(self, event_type):
        """
        When light bulb is off,
        color control must not be allowed
        """
        return (not self.state) and (event_type is EVENT_COLOR)

    def update_light(self, event_type, value=None, need_command=True):
        if self.is_invalid_command(event_type):
            print("This is invalid command")
            return

        # set value
        if event_type is EVENT_TOGGLE:
            if value is not None and bool(value) != self.state:
                self.textBrowserLog.append(
                    f'[Recv] {self.log_text.get(event_type)} {self.toogle_text.get(bool(value))}')
                self.toggle_update_from_remote = True
                self.pushButtonStatus.toggle()
        elif event_type is EVENT_DIMMING:
            if value is not None and value != self.dimming_level:
                self.textBrowserLog.append(
                    f'[Recv] {self.log_text.get(event_type)} {round(value/LIGHTBULB_DIM_ST_CONVERT*100)}{LIGHTBULB_DIM_UNIT}')
            self.dimming_level = round(value/LIGHTBULB_DIM_ST_CONVERT*100) if value else self.horizontalSliderDimming.value()

        elif event_type is EVENT_COLOR:
            if value is not None and value != self.color_level:
                self.textBrowserLog.append(
                    f'[Recv] {self.log_text.get(event_type)} {int(round(1000000/value, 0)) }{LIGHTBULB_COLOR_TEMP_UNIT}')
            # We have to convert color level
            self.color_level = int(
                round(1000000/value, 0)) if value else self.horizontalSliderColorTemp.value()
        else:
            return

        # ui update
        self.update_ui()

        # send command
        if need_command:
            self.send_command(event_type)

    def event_handler(self, event):
        event_type = None
        try:
            if 'onoff' in event:
                event_type = EVENT_TOGGLE
            elif 'level' in event:
                event_type = EVENT_DIMMING
            elif 'colortemp' in event:
                event_type = EVENT_COLOR
        except (IndexError, ValueError):
            self.textBrowserLog.append(
                'Error: Invalid event format - ' + event)
        if event_type:
            value = event.split(":")[1]
            self.update_light(event_type, int(value), False)

    def autotest_event_handler(self, used_device):
        self.horizontalSliderColorTemp.setEnabled(not used_device)
        self.horizontalSliderDimming.setEnabled(not used_device)
        self.pushButtonStatus.setEnabled(not used_device)
