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
# File : common_window.py
# Description: Initiate common window structure for end device types

from common.utils import Utils
from common.device_command import *
from common.manage_device import *
from common.process_controller import *
from common.ioterPipe import PipeThread
from auto_onboarding.autod import *

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *

## Common Window class ##
class CommonWindow(QMainWindow):
    dialog_closed = pyqtSignal(str)
    occur_abort = pyqtSignal(str)
    update_onboarding = pyqtSignal(int, str, str)
    ## Initialize Common Window class ##
    def __init__(self, view_name, icon_name, device_info, parent, window_manager):
        super().__init__()

        self.parent = parent
        self.device_info = device_info
        self.ioter = ProcessController()
        self.force_quit = False
        self.pipeThread = 0
        self.pipe_event_handler = None
        self.initial_value_handler = None
        self.autotest_event_handler = None
        self.auto = self.device_info.get_auto()
        self.is_slider_pressed = False
        self.level = 0

        self.ioter.terminate_chip_all_clusters(self.device_info, True)
        self.init_ui_component(view_name, icon_name, device_info)

        self.origin_width = self.frameGeometry().width()
        self.origin_height = self.frameGeometry().height()
        self.window_manager = window_manager
        self.winSet(self.origin_width, self.origin_height)
        self.cur_pos = None
        self.polling_time_ms = 50
        self.initPositionTimer()

        self.show()
        self.savePos()
    ## Initialize Common Window UX component ##
    def init_ui_component(self, view_name, icon_name, device_info):
        self.ui = uic.loadUi(Utils.get_view_path(view_name), self)
        title = f'{CommandUtil.get_device_type_by_device_id(device_info.device_id)}-{device_info.device_num}'
        if device_info.ioter_name is not None:
            title = title[:-1] + " Binary : " + device_info.ioter_name
        self.title = title
        self.setWindowTitle(title)
        self.init_icon(icon_name)
        self.init_power_button()
        self.init_auto_checkbox()
        self.init_information_ui(device_info)
        if not(view_name == "light.ui" or view_name == "onoffplugin.ui"):
            self.init_battery_slider()
        self.spinboxBattery.installEventFilter(self)
        self.stackedWidget.setCurrentIndex(0)

    ## Initialize Common Window icon ##
    def init_icon(self, icon_name):
        self.labelDevicePicture.setMinimumSize(QSize(0, 90))
        self.labelDevicePicture.setAlignment(Qt.AlignCenter)
        self.labelDevicePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path(icon_name), 70, 70))

    ## Initialize Common Window toggle button ##
    def init_toggle_button(self):
        self.pushButtonStatus.setMinimumSize(QSize(0, 30))
        self.pushButtonStatus.setCheckable(True)
        self.pushButtonStatus.setStyleSheet(
            Utils.get_ui_style_toggle_btn(False))

    ## Initialize Common Window auto checkbox ##
    def init_auto_checkbox(self):
        self.chkbox_auto.stateChanged.connect(
            self.check_conditions_for_auto_onboarding)

    ## Initialize Common Window power button ##
    def init_power_button(self):
        self.pushButtonDevicePower.setMinimumSize(QSize(0, 34))
        self.pushButtonDevicePower.setCheckable(True)
        self.pushButtonDevicePower.toggled.connect(self.power_onoff)

    ## Initialize Common Window information ui ##
    def init_information_ui(self, device_info):
        self.plainTextEditThreadVersion.setMinimumSize(QSize(0, 34))
        self.plainTextEditComport.setMinimumSize(QSize(0, 34))
        self.pushButtonDevicePower.setMinimumSize(QSize(0, 34))
        self.progressBar.setMinimumSize(QSize(0, 35))
        self.plainTextEditPairingCode.setMinimumSize(QSize(0, 35))
        self.progressBar.setValue(0)
        self.plainTextEditThreadVersion.setPlainText(
            device_info.get_thread_type())
        self.plainTextEditThreadVersion.setReadOnly(True)
        self.plainTextEditComport.setPlainText(device_info.com_port)
        self.plainTextEditComport.setReadOnly(True)
        self.plainTextEditDebugLevel.setPlainText(device_info.debug_level)
        self.plainTextEditDebugLevel.setReadOnly(True)
        self.plainTextEditPairingCode.setPlainText("0")
        self.plainTextEditPairingCode.setReadOnly(True)

    def init_battery_slider(self):
        self.horizontalSliderBattery.setRange(
            int(BATTERY_MIN_VAL), int(BATTERY_MAX_VAL))
        self.spinboxBattery.setRange(
            int(BATTERY_MIN_VAL), int(BATTERY_MAX_VAL))
        self.horizontalSliderBattery.setSingleStep(
            self.get_slider_single_step(BATTERY_MIN_VAL, BATTERY_MAX_VAL))
        self.horizontalSliderBattery.setValue(int(self.level))
        self.horizontalSliderBattery.sliderPressed.connect(
            self.sliderPressed)
        self.horizontalSliderBattery.sliderReleased.connect(
            self.sliderReleased)
        self.horizontalSliderBattery.valueChanged.connect(
            self.valueChanged)
        self.horizontalSliderBattery.setStyleSheet(
            Utils.get_ui_style_slider("COMMON"))
        
    def valueChanged(self):
        if self.is_slider_pressed:
            self.spinboxBattery.setValue(
                self.horizontalSliderBattery.value())
            return
        if not self.is_slider_pressed:
            level = self.horizontalSliderBattery.value()
            # print(f'valueChanged : old ({self.level}), new ({level})')
            if self.level != level:
                self.update_battery_sensor()

    def sliderPressed(self):
        self.is_slider_pressed = True

    def sliderReleased(self):
        self.is_slider_pressed = False
        level = self.horizontalSliderBattery.value()
        if self.level != level:
            self.update_battery_sensor()

    def set_battery_level(self, level=None):
        if level is not None:
            self.level = level
        else:
            self.level = self.horizontalSliderBattery.value()
        self.level = max(min(self.level, BATTERY_MAX_VAL),
                         BATTERY_MIN_VAL)

    def update_ui(self):
        self.horizontalSliderBattery.setValue(int(self.level))
        self.spinboxBattery.setValue(self.level)

    def update_battery_sensor(self, level=None, need_command=True):
        self.set_battery_level(level)
        self.update_ui()
        # self.set_state()
        if need_command:
            BatteryCommand.remain(self.device_info.device_num, self.level)
            self.textBrowserLog.append(
                f'[Send] {self.level}{BATTERY_UNIT}')
            
    def eventFilter(self, obj, event):
        if obj is self.spinboxBattery and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                level = self.spinboxBattery.value()
                self.update_battery_sensor(level)
                return True
        return super().eventFilter(obj, event)
    
    ## Toggle button handler ##
    def add_toggle_button_handler(self, handler):
        self.pushButtonStatus.toggled.connect(handler)

    ## Pipe event handler ##
    def add_pipe_event_handler(self, handler):
        self.pipe_event_handler = handler

    ## Initial value handler ##
    def add_initial_value_handler(self, handler):
        self.initial_value_handler = handler
    ## Autotest event handler ##
    def add_autotest_event_handler(self, handler):
        self.autotest_event_handler = handler

    ##  Calculate slider single step ##
    def get_slider_single_step(self, min, max):
        return int((max - min) / 100)

    ## Update progress bar ##
    def update_progress(self, step, msg):
        self.progressBar.setValue(int(step))
        if not self.device_info.get_commissioning_state():
            self.textBrowserLog.append(msg)
        if step == 100:  # commissioning complete
            self.stackedWidget.setCurrentIndex(1)
            self.device_info.set_commissioning_state(True)
            if self.initial_value_handler:
                self.initial_value_handler()
        elif step == 1:
            self.device_info.set_commissioning_state(False)
            if self.chkbox_auto.isChecked():
                self.auto_go()
        elif step == 80 and self.device_info.get_commissioning_state():
            self.stackedWidget.setCurrentIndex(1)
            self.progressBar.setValue(100)

    ## Set Power state On/off ##
    @pyqtSlot(bool)
    def power_onoff(self, state):
        self.pushButtonDevicePower.setText(
            {True: "Power Off", False: "Power On"}[state])
        if state:
            self.stackedWidget.setCurrentIndex(0)
            self.ioter.launch_chip_all_clusters(self.device_info)
            self.textBrowserLog.append("=== Matter Commissioning ===")

            self.pipeThread = PipeThread(self.device_info.device_num)
            # custom signal from PipeThread to main thread
            self.pipeThread.msg_changed.connect(self.update_msg)
            self.pipeThread.start()
        else:
            self.pushButtonDevicePower.setEnabled(False)
            self.textBrowserLog.append("=== Power off takes 10 sec ===")
            print("=== Power off takes 10 sec ===")
            QCoreApplication.processEvents()
            if self.device_info.get_commissioning_state():
                self.ioter.terminate_chip_all_clusters(self.device_info, False)
            else:
                self.ioter.terminate_chip_all_clusters(self.device_info, True)
            self.stackedWidget.setCurrentIndex(2)
            self.pushButtonDevicePower.setEnabled(True)
            if self.chkbox_auto.isChecked():
                self.auto_remove()

    ## Receive msg from ioterPipe.pipeThread and update ##
    @pyqtSlot(str)
    def update_msg(self, str):  # received msg from ioterPipe.pipeThread
        if str.find('step') >= 0:
            token = str.split(":")
            self.update_progress(int(token[1]), token[2])
        elif str.find('pair') >= 0:
            self.plainTextEditPairingCode.setPlainText(
                Utils.get_setup_code(str))
        elif str.find('qrcode') >= 0:
            self.QRcode.setPixmap(Utils.get_qrcode_img(str, 150, 150))
        elif str.find('threadsettingfile') >= 0:
            self.device_info.set_thread_setting_file(str.split(":")[1])
        elif str.find('abort') >= 0:
            # logging.info(str)
            isPowerOn = self.pushButtonDevicePower.isChecked()
            if isPowerOn and not self.force_quit:
                self.textBrowserLog.append(str)
                self.pushButtonDevicePower.toggle()
                self.occur_abort.emit(self.device_info.com_port)
        else:
            if self.pipe_event_handler is not None:
                self.pipe_event_handler(str)

    # Handle close event ##
    # must not rename closeEvent ##
    def closeEvent(self, event):
        if not self.force_quit:
            re = QMessageBox.question(self, "Exit", "Do you want to exit?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if re == QMessageBox.Yes:
                self.timer = None
                self.winRemove()
                self.force_closeEvent()
                event.accept()
            else:
                event.ignore()
        else:
            self.timer = None
            self.winRemove()

    ## Handle key press event ##
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.closeEvent(QCloseEvent())

    ## Handle force close event ##
    def force_closeEvent(self, device=ForceClose.DEVICES):
        if (device & ForceClose.DEVICES) and not self.force_quit:
            print('quit deviceNumber: %s port:%s' %
                (self.device_info.device_num, self.device_info.com_port))
            self.dialog_closed.emit(self.device_info.com_port)
            self.auto.disconnect_device(self.device_info.device_num)
            self.ioter.terminate_chip_all_clusters(self.device_info, True)
            if self.pipeThread:
                self.pipeThread.stop()
            self.force_quit = True
            self.close()
            self.parent.close()

    ## Auto remove device ##
    def auto_remove(self):
        if self.device_info.get_commissioning_state():
            self.auto.request_remove(
                self.device_info.com_port, self.device_info.device_num, self.device_info.device_id)
        else:
            self.auto.disconnect_device(self.device_info.device_num)

    ## Verify auto onboarding request ##
    def auto_go(self):
        if not self.auto.request_onboarding(self.device_info.com_port, self.device_info.device_num, self.plainTextEditPairingCode.toPlainText(), self.device_info.device_id):
            self.textBrowserLog.append("Can't work auto-onboarding")
            self.chkbox_auto.toggle()
            self.pushButtonDevicePower.toggle()

    ## Check if device is used in Automation ##
    def autotest_used(self, use):
        if self.autotest_event_handler is not None:
            self.autotest_event_handler(use)
        if use:
            title = "In Use in Automation Test - " + self.title
            self.setWindowTitle(title)
            self.pushButtonDevicePower.setEnabled(False)
        else:
            self.setWindowTitle(self.title)
            self.pushButtonDevicePower.setEnabled(True)

    ## Check auto onboarding state ##
    @pyqtSlot(int, str, str)
    def auto_onboarding_state(self, state, comPort, device_num):
        if self.force_quit:
            return
        if state == STOnboardingResult.ONBOARDING_FAILURE:
            if self.device_info.device_num == device_num:
                self.device_info.set_commissioning_state(False)
                self.textBrowserLog.append("=== Onboarding failed ===")
        elif state == STOnboardingResult.REMOVED_PHONE:
            if self.chkbox_auto.isChecked():
                self.chkbox_auto.toggle()

    ## Check conditions for auto onboarding ##
    def check_conditions_for_auto_onboarding(self):
        if not self.chkbox_auto.isChecked():
            self.setWindowTitle(self.title)
        elif not self.device_info.deviceManager.usb_manager.connected_phone_device():
            QMessageBox.critical(
                self, "Error", "Can't work auto-onboarding because the phone is not connected")
            self.chkbox_auto.toggle()
        else:
            title = "In Use in Auto Onboarding - " + self.title
            self.setWindowTitle(title)

    ## Handle window position ##
    def winSet(self, w, h):
        x, y = self.window_manager.add(w, h)
        if x is not None:
            print("MOVE to", x, y)
            self.move(x, y)
        else:
            print("Cannot find a empty space", self.frameGeometry())
        print('winSet()', self.frameGeometry())

    ## Save window postion ##
    def savePos(self):
        self.cur_pos = self.frameGeometry()

    ## Move window position ##
    def winMove(self, x, y):
        self.winRemove()
        self.window_manager.addWithPosition(x, y, self.cur_pos.width(), self.cur_pos.height())

    ## Remove window position from window manager ##
    def winRemove(self, fg=None):
        if fg is None:
            fg = self.cur_pos
        self.window_manager.remove(fg.x(), fg.y(), fg.width(), fg.height())

    ## Handle move event ##
    def moveEvent(self, event):
        if self.timer is not None:
            self.timer.start(self.polling_time_ms)

    ## Check window postion ##
    def checkPosition(self):
        if self.timer is not None and not self.timer.isActive():
            return
        if self.frameGeometry() == self.cur_pos:
            self.timer.stop()
            print('Window stopped moving', self.frameGeometry())

            self.winMove(self.frameGeometry().x(), self.frameGeometry().y())
            self.savePos()
        else:
            self.winRemove()
            self.savePos()

    ## Initilize Position Timer ##
    def initPositionTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkPosition)
        self.timer.start(self.polling_time_ms)
