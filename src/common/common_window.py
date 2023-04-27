from common.utils import Utils
from common.device_command import CommandUtil
from common.manage_device import *
from common.process_controller import *
from common.ioterPipe import PipeThread
from auto_onboarding.autod import *

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class CommonWindow(QMainWindow):
    dialog_closed = pyqtSignal(str)
    occur_abort = pyqtSignal(str)
    update_onboarding = pyqtSignal(int, str, str)

    def __init__(self, view_name, icon_name, device_info, parent, window_manager):
        super().__init__()

        self.parent = parent
        self.device_info = device_info
        self.ioter = ProcessController()
        self.force_quit = False
        self.pipeThread = 0
        self.pipe_event_handler = None
        self.autotest_event_handler = None
        self.auto = self.device_info.get_auto()

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

    def init_ui_component(self, view_name, icon_name, device_info):
        self.ui = uic.loadUi(Utils.get_view_path(view_name), self)
        title = f'{CommandUtil.get_device_type_by_device_id(device_info.device_id)}-{device_info.device_num}'
        if device_info.ioter_name is not None:
            title = title[:-1] + " Binary : " + device_info.ioter_name + "]"
        self.title = title
        self.setWindowTitle(title)
        self.init_icon(icon_name)
        self.init_power_button()
        self.init_auto_checkbox()
        self.init_information_ui(device_info)
        self.stackedWidget.setCurrentIndex(0)

    def init_icon(self, icon_name):
        self.labelDevicePicture.setMinimumSize(QSize(0, 90))
        self.labelDevicePicture.setAlignment(Qt.AlignCenter)
        self.labelDevicePicture.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path(icon_name), 70, 70))

    def init_toggle_button(self):
        self.pushButtonStatus.setMinimumSize(QSize(0, 30))
        self.pushButtonStatus.setCheckable(True)
        self.pushButtonStatus.setStyleSheet(
            Utils.get_ui_style_toggle_btn(False))

    def init_auto_checkbox(self):
        self.chkbox_auto.stateChanged.connect(
            self.check_conditions_for_auto_onboarding)

    def init_power_button(self):
        self.pushButtonDevicePower.setMinimumSize(QSize(0, 34))
        self.pushButtonDevicePower.setCheckable(True)
        self.pushButtonDevicePower.toggled.connect(self.power_onoff)

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
        self.plainTextEditPairingCode.setReadOnly(True)

    def add_toggle_button_handler(self, handler):
        self.pushButtonStatus.toggled.connect(handler)

    def add_pipe_event_handler(self, handler):
        self.pipe_event_handler = handler

    def add_autotest_event_handler(self, handler):
        self.autotest_event_handler = handler

    def get_slider_single_step(self, min, max):
        return int((max - min) / 100)

    def update_progress(self, step, msg):
        self.progressBar.setValue(int(step))
        if not self.device_info.get_commissioning_state():
            self.textBrowserLog.append(msg)
        if step == 100:  # commissioning complete
            self.stackedWidget.setCurrentIndex(1)
            self.device_info.set_commissioning_state(True)
            if self.pipe_event_handler is not None:
                self.pipe_event_handler(msg)
        elif step == 1:
            self.device_info.set_commissioning_state(False)
            if self.chkbox_auto.isChecked():
                self.auto_go()
        elif step == 80 and self.device_info.get_commissioning_state():
            self.stackedWidget.setCurrentIndex(1)
            self.progressBar.setValue(100)

    @pyqtSlot(bool)
    def power_onoff(self, state):
        self.pushButtonDevicePower.setText(
            {True: "Power Off", False: "Power On"}[state])
        if state:
            self.stackedWidget.setCurrentIndex(0)
            self.ioter.launch_chip_all_clusters(self.device_info)
            self.textBrowserLog.append("=== Matter Commissioning ===")

            # self??WindowClass???�스?�스, Thread ?�래?�에??parent�??�달
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

    # must not rename closeEvent
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.closeEvent(QCloseEvent())

    def force_closeEvent(self):
        print('quit deviceNumber: %s port:%s' %
              (self.device_info.device_num, self.device_info.com_port))
        self.dialog_closed.emit(self.device_info.com_port)
        self.auto_remove()
        self.ioter.terminate_chip_all_clusters(self.device_info, True)
        if self.pipeThread:
            self.pipeThread.stop()
        self.force_quit = True
        self.close()
        self.parent.close()

    def auto_remove(self):
        if self.device_info.get_commissioning_state():
            self.auto.request_remove(
                self.device_info.com_port, self.device_info.device_num, self.device_info.device_id)
        else:
            self.auto.disconnect_device(self.device_info.device_num)

    def auto_go(self):
        if not self.auto.request_onboarding(self.device_info.com_port, self.device_info.device_num, self.plainTextEditPairingCode.toPlainText(), self.device_info.device_id):
            self.textBrowserLog.append("Can't work auto-onboarding")
            self.chkbox_auto.toggle()
            self.pushButtonDevicePower.toggle()

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

    @pyqtSlot(int, str, str)
    def auto_onboarding_state(self, state, comPort, device_num):
        if state == ONBOARDING_FAILURE:
            if self.device_info.device_num == device_num:
                self.device_info.set_commissioning_state(False)
                self.textBrowserLog.append("=== Onboarding failed ===")
        elif state == REMOVED_PHONE:
            if self.chkbox_auto.isChecked():
                self.chkbox_auto.toggle()

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

    def winSet(self, w, h):
        x, y = self.window_manager.add(w, h)
        if x is not None:
            print("MOVE to", x, y)
            self.move(x, y)
        else:
            print("Cannot find a empty space", self.frameGeometry())
        print('winSet()', self.frameGeometry())

    def savePos(self):
        self.cur_pos = self.frameGeometry()

    def winMove(self, x, y):
        self.winRemove()
        self.window_manager.addWithPosition(x, y, self.cur_pos.width(), self.cur_pos.height())

    def winRemove(self, fg=None):
        if fg is None:
            fg = self.cur_pos
        self.window_manager.remove(fg.x(), fg.y(), fg.width(), fg.height())

    def moveEvent(self, event):
        if self.timer is not None:
            self.timer.start(self.polling_time_ms)

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

    def initPositionTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkPosition)
        self.timer.start(self.polling_time_ms)
