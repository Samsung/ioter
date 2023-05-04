#!/usr/bin/python
from common.device_command import *
from common.device_window import *
from common.manage_device import *
from common.manage_usb import UsbMonitor
from common.utils import Utils
from common.config import Config
from common.help_window import *
from automation.automationmain import automationWindow
from auto_onboarding.autod import *
from auto_onboarding.auto_onboardingmain import auto_onboardingWindow
from typing import Final
from winman import window_manager

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *

sys.path.append('automation')

IOTER_NAME: Final = 'ioter'

class MainWindow(QMainWindow,
                 uic.loadUiType(Utils.get_view_path('main.ui'))[0]):
    force_close = pyqtSignal(int)
    send_msg_about_onboarding = pyqtSignal(int, str, str)
    removed_usb = pyqtSignal(str)

    def __init__(self, window_manager):
        super().__init__()
        self.setupUi(self)

        self.dialog = dict()
        self.automation = None
        self.auto_onboarding = None
        self.setWindowTitle(IOTER_NAME)
        self.set_logo()
        self.removedDeviceNumber = -1
        self.pushButtonStart.clicked.connect(self.start_click)
        self.actionAutomation.triggered.connect(self.start_automation)
        self.actionAutomation.setShortcut("Ctrl+A")
        self.actionAuto_onboarding.triggered.connect(
            self.start_auto_onboarding)
        self.actionAuto_onboarding.setShortcut("Ctrl+Z")
        self.actionAbout.triggered.connect(self.start_help)
        self.deviceManager = DeviceManager()
        self.display_comport()
        self.display_threadType()
        self.display_deviceType()

        self.usbMonitor = UsbMonitor()
        self.usbMonitor.usb_changed.connect(self.display_comport)
        self.usbMonitor.start()

        self.auto = autoDevice(self)
        self.auto.update_onboarding_state.connect(self.auto_onboarding_state)
        if self.deviceManager.usb_manager.connected_phone_device():
            self.auto.start()

        self.use_test_window = False
        discriminator = Utils.generate_random_discriminator()
        self.spinBoxDiscriminator.setValue(discriminator)

        self.window_manager = window_manager
        self.cur_pos = None
        self.polling_time_ms = 50
        self.initPositionTimer()
        self.savePos()
        self.checkDir()

        Config.load()
        self.test_window_click_count = 0
        self.labelMatterlogo.mousePressEvent = self.on_label_matterlogo_clicked
        self.actionTestWindow.setVisible(Config.test_window_shown)
        self.test_window_timer = QTimer()
        self.test_window_timer.setInterval(10000)
        self.test_window_timer.timeout.connect(self.reset_test_window_count)

    def on_label_matterlogo_clicked(self, event):
        if self.actionTestWindow.isVisible():
            return

        self.test_window_click_count += 1
        if self.test_window_click_count == 10:
            self.actionTestWindow.setVisible(True)
            print("Test Window OPEN in upper option bar")
            Config.test_window_shown = True
            Config.save()
            QMessageBox.about(self,'Test Window','Test Window mode is now available.')

        if not self.test_window_timer.isActive():
            self.test_window_timer.start()

    def reset_test_window_count(self):
        self.test_window_click_count = 0
        self.test_window_timer.stop()
        self.popup_shown = False

    def create_dialog(self, obj, cls_name):
        if obj is None:
            obj = cls_name(self)
            obj.dialog_closed.connect(self.exit_dialog)
            self.force_close.connect(obj.force_closeEvent)
            obj.show()
        else:
            print("Already Opened")
        return obj

    def start_automation(self):
        device_list = self.deviceManager.get_used_devices()
        isonboarded = False
        for device in device_list:
            if device.get_commissioning_state():
                isonboarded = True
                break

        if isonboarded:
            self.automation = self.create_dialog(self.automation, automationWindow)
            self.automation.send_used_list.connect(self.autotest_used_list)
            self.removed_usb.connect(self.automation.removed_device)
        else:
            print('No Devices are Connected/Onboarded')
            automationWindow.errorbox('No Devices are Connected/Onboarded')

    @pyqtSlot(int, str, str)
    def auto_onboarding_state(self, state, comPort, device_num):
        print(f'state {state} comport {comPort} device_num {device_num}')
        self.send_msg_about_onboarding.emit(state, comPort, device_num)

    def start_auto_onboarding(self):
        self.auto_onboarding = self.create_dialog(self.auto_onboarding, auto_onboardingWindow)
        self.send_msg_about_onboarding.connect(self.auto_onboarding.update_status)

    def start_help(self):
        self.help = HelpWindow(self, IOTER_NAME)
        self.help.show()

    def set_logo(self):
        self.labelMatterlogo.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path('ioter_logo.png'), 100, 15))
        self.labelDeviceIcon.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path('devices.png'), 50, 50))

    def check_start_button(self):
        comPort = self.comboBoxCom.currentText()
        deviceNum = self.deviceManager.get_device_number()
        discriminator = self.spinBoxDiscriminator.value()

        if comPort == 'None' or len(deviceNum) == 0 or discriminator == '':
            self.pushButtonStart.setDisabled(True)
        else:
            self.pushButtonStart.setEnabled(True)

    @pyqtSlot(str, str)
    # received msg from ioterPipe.Thread1
    def display_comport(self, action=None, path=None):
        if action == 'add':
            comPort = self.deviceManager.add_usb_device(path)
            if comPort and self.auto_onboarding:
                self.auto_onboarding.add_device(
                    comPort, self.deviceManager.get_device_vendor(comPort))
            if self.deviceManager.usb_manager.connected_phone_device():
                if not self.auto.is_running():
                    self.auto.start()
        elif action == 'remove':
            comPort = self.deviceManager.remove_usb_device(path)
            if comPort in self.dialog:
                self.dialog[comPort].get_window().force_closeEvent()
                if self.automation:
                    self.removed_usb.emit(
                        self.dialog[comPort].device_info.get_device_num())
                del (self.dialog[comPort])
            if self.auto_onboarding:
                self.auto_onboarding.remove_device(comPort)
            if not self.deviceManager.usb_manager.connected_phone_device():
                if self.auto.is_running():
                    self.auto.stop()
        comport_list = self.deviceManager.get_unused_devices()
        self.comboBoxCom.clear()
        if len(comport_list) == 0:
            self.comboBoxCom.addItem('None')
        else:
            for comport in comport_list:
                self.comboBoxCom.addItem(
                    f"{comport}/{self.deviceManager.get_device_vendor(comport)}")
        self.check_start_button()

    def display_threadType(self):
        list = os.listdir(Utils.get_thread_lib_path())
        filtered_list = [thread for thread in list if thread.startswith(
            Utils.get_thread_lib_prefix())]
        for file in filtered_list:
            self.comboBoxThread.addItem(
                file[len(Utils.get_thread_lib_prefix()):])

    def display_deviceType(self):
        CommandUtil.device_type_id.keys()
        self.comboBoxDevice.addItems(CommandUtil.device_type_id.keys())

    def display_ioterName(self):
        items = []
        list = os.listdir(Utils.get_ioter_path())
        filtered_list = [ioter for ioter in list if ioter.startswith(
            Utils.get_ioter_prefix())]
        for file in filtered_list:
            items.append(file[len(Utils.get_ioter_prefix()):])
        item_data, ok = QInputDialog.getItem(
            self, 'Select binary', 'Select the chip-all-clusters-app', items)

        if ok:
            print('ioterName :' + item_data)
            return item_data
        else:
            return None

    def start_click(self):
        """
        commission start 구현
        """
        deviceNum = str(self.deviceManager.get_device_number()[0])
        discriminator = self.spinBoxDiscriminator.value()
        threadType = self.comboBoxThread.currentText()
        comPort = self.comboBoxCom.currentText().split('/')[0]
        debugLevel = self.comboBoxDebug.currentText()
        device_type = self.comboBoxDevice.currentText()

        if self.create_device_window(deviceNum, discriminator, threadType, comPort, debugLevel, device_type):
            if self.auto_onboarding is not None:
                self.auto_onboarding.remove_device(comPort)

    def create_device_window(self, deviceNum, discriminator, threadType, comPort, debugLevel, device_type):
        print(
            f"create_device_window - device number : {deviceNum} com port : {comPort}")
        ioterName = None

        if comPort in self.dialog:
            print(comPort + " is already in use")
            return False

        if self.actionDeveloper.isChecked() or "build" in threadType:
            ioterName = self.display_ioterName()
            if ioterName is None:
                return False

        if self.actionTestWindow.isChecked():
            self.use_test_window = True
        else:
            self.use_test_window = False

        device_info = DeviceInfo(
            deviceNum, discriminator, threadType, comPort, debugLevel, ioterName, self.deviceManager, CommandUtil.get_device_id_by_device_type(device_type), self.auto)
        self.dialog[comPort] = get_device_window_by_device_type(
            device_type, device_info, self.use_test_window, self.window_manager)
        if (self.dialog[comPort] is None):
            return False

        self.dialog[comPort].get_window(
        ).dialog_closed.connect(self.exit_dialog)
        self.dialog[comPort].get_window().occur_abort.connect(self.reset_usb)
        self.force_close.connect(
            self.dialog[comPort].get_window().force_closeEvent)
        self.send_msg_about_onboarding.connect(
            self.dialog[comPort].get_window().auto_onboarding_state)
        if self.deviceManager.set_used_device(comPort, device_info) is None:
            print("set_used_device is fail")
        self.display_comport()
        self.spinBoxDiscriminator.setValue((discriminator+1) & 0xFFF)
        return True

    @pyqtSlot(str)
    def exit_dialog(self, comPort):
        print('exit_dialog : ' + comPort)
        if comPort == "Automation":
            if self.automation:
                del self.automation
                self.automation = None
        elif comPort == "auto_onboarding":
            if self.auto_onboarding:
                del self.auto_onboarding
                self.auto_onboarding = None
        elif comPort == "auto_onboarding_all":
            if self.auto_onboarding:
                del self.auto_onboarding
                self.auto_onboarding = None
                self.force_close.emit(ForceClose.DEVICES)
        elif self.deviceManager.set_unused_device(comPort):
            del (self.dialog[comPort])
            self.display_comport()
            if self.auto_onboarding:
                self.auto_onboarding.add_device(
                    comPort, self.deviceManager.get_device_vendor(comPort))
        else:
            print("set_unused_device is fail")

    @pyqtSlot(dict)
    def autotest_used_list(self, used_device_dict):
        print("used_list : ", used_device_dict.items())
        for device_num in used_device_dict.items():
            device_info = self.deviceManager.get_device_info_by_device_num(
                int(device_num[0]))
            comPort = device_info.get_com_port()
            self.dialog[comPort].get_window().autotest_used(device_num[1])

    @pyqtSlot(str)
    def reset_usb(self, comPort):
        print('reset_usb :' + comPort)
        self.deviceManager.reset_device(comPort)

    # must not rename closeEvent
    def closeEvent(self, event):
        # print('closeEvent : ')
        re = QMessageBox.question(self, "Exit", "Do you want to exit?",
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if re == QMessageBox.Yes:
            self.usbMonitor.stop()
            self.force_close.emit(ForceClose.ALL)
            self.auto.update_onboarding_state.disconnect(self.auto_onboarding_state)
            self.auto.stop()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def savePos(self):
        self.cur_pos = self.frameGeometry()

    def winMove(self, x, y):
        fg = self.frameGeometry()
        self.winRemove(fg)
        self.window_manager.addWithPosition(
            x, y, self.frameGeometry().width(), self.frameGeometry().height())

    def winRemove(self, fg=None):
        if fg is None:
            fg = self.cur_pos
        self.window_manager.remove(fg.x(), fg.y(), fg.width(), fg.height())

    def moveEvent(self, event):
        self.timer.start(self.polling_time_ms)

    def checkPosition(self):
        if self.timer and not self.timer.isActive():
            return
        if self.frameGeometry() == self.cur_pos:
            self.timer.stop()
            print('Window stopped moving', self.frameGeometry())

            self.winRemove()
            self.winMove(self.frameGeometry().x(), self.frameGeometry().y())
            self.savePos()
        else:
            self.winRemove()
            self.savePos()

    def initPositionTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkPosition)
        self.timer.start(self.polling_time_ms)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F12:
            self.window_manager.showGuide()
            self.window_manager.dumpRectangles()

    def checkDir(self):
        if not os.path.isdir(Utils.get_tmp_path()):
            os.mkdir(Utils.get_tmp_path())
        if not os.path.isdir(Utils.get_screenshot_path()):
            os.mkdir(Utils.get_screenshot_path())


if __name__ == '__main__':
    # don't auto scale when drag app to a different monitor.
    # QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setStyleSheet('''
    QWidget {
      font-size: 15px;
    }
  ''')
    screen = QDesktopWidget().availableGeometry()
    wm = window_manager.WindowManager(
        screen.x(), screen.y(), screen.width(), screen.height())
    mainWindow = MainWindow(wm)
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')
