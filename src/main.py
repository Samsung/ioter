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
# File : main.py
# Description:
# Auto onboarding, automation of IoT test scenarios and UI Window Management

#!/usr/bin/python
from common.device_command import *
from common.device_window import *
from common.manage_device import *
from common.manage_usb import UsbMonitor
from common.utils import Utils
from common.config import Config
from common.help_window import HelpWindow
from common.log import Log, LogFile
from automation.automationmain import automationWindow
from auto_onboarding.autod import *
from auto_onboarding.auto_onboardingmain import auto_onboardingWindow
from typing import Final
from winman import window_manager

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from packaging import version

sys.path.append('automation')

IOTER_NAME: Final = 'ioter'

## Main Window class ##
class MainWindow(QMainWindow,
                 uic.loadUiType(Utils.get_view_path('main.ui'))[0]):
    force_close = pyqtSignal(int)
    send_msg_about_onboarding = pyqtSignal(int, str, str)
    removed_usb = pyqtSignal(str)

    ## Initialize Main Window class ##
    def __init__(self, window_manager):
        super().__init__()

        # Pre Main
        Utils.remove_data_files()

        # Start Main
        self.setupUi(self)

        self.dialogs = dict()
        self.automation = None
        self.auto_onboarding = None
        self.setWindowTitle(IOTER_NAME)
        self.set_logo()
        self.removedDeviceNumber = -1
        self.pushButtonStart.clicked.connect(self.start_click)
        self.pushButtonStart.setStyleSheet(
            Utils.get_ui_style_toggle_btn(False))
        self.actionAutomation.triggered.connect(self.start_automation)
        self.actionAutomation.setShortcut("Ctrl+A")
        self.actionAuto_onboarding.triggered.connect(
            self.start_auto_onboarding)
        self.actionAuto_onboarding.setShortcut("Ctrl+Z")
        self.actionAbout.triggered.connect(self.start_help)
        self.actionMulti_BT_mode.triggered.connect(self.check_multi_bt_mode)
        self.deviceManager = DeviceManager()
        self.display_comport()
        self.display_threadType()
        self.display_deviceType()

        self.usbMonitor = UsbMonitor()
        self.usbMonitor.usb_changed.connect(self.display_comport)
        self.usbMonitor.start()

        self.auto_onboarding_thread = autoDevice(self)
        self.auto_onboarding_thread.update_onboarding_state.connect(self.auto_onboarding_state)
        if self.deviceManager.usb_manager.connected_phone_device():
            self.auto_onboarding_thread.start()

        self.use_test_window = False
        discriminator = Utils.generate_random_discriminator()
        self.spinBoxDiscriminator.setValue(discriminator)
        # self.spinBoxDiscriminator.setStyleSheet(
        #     Utils.get_ui_style_spinbox())

        self.window_manager = window_manager
        self.cur_pos = None
        self.polling_time_ms = 50
        self.initPositionTimer()
        self.savePos()

        self.default_config = Config()
        self.default_config_apply()
        self.option_menu_click_count = 0
        self.labelMatterlogo.mousePressEvent = self.on_label_matterlogo_clicked

    ## Apply default configurations ##
    def default_config_apply(self):
        conf = self.default_config
        self.option_menu_shown = conf.option_menu_shown if conf.option_menu_shown else False
        self.menuOption.menuAction().setVisible(conf.option_menu_shown)
        self.auto_onboarding_thread.debug = conf.auto_onboarding_debug_mode if conf.auto_onboarding_debug_mode else False
        self.default_thread_debug_level = conf.thread_debug_level if conf.thread_debug_level >= 1 and conf.thread_debug_level <= 5 else 4
        self.default_set_thread_debug_level(self.comboBoxDebug)
        self.default_thread_type = conf.default_thread_type if conf.default_thread_type in ['fed','med','sed'] else 'fed'
        self.default_set_thread_type(self.comboBoxThread)
        self.multi_bt_mode = conf.multi_bt_mode if conf.multi_bt_mode else False
        if self.multi_bt_mode:
            if not self.actionMulti_BT_mode.isChecked():
                self.actionMulti_BT_mode.toggle()
        else:
            if self.actionMulti_BT_mode.isChecked():
                self.actionMulti_BT_mode.toggle()

    ## Set default thread debug level ##
    def default_set_thread_debug_level(self, comboBoxObj):
        if comboBoxObj.findText(f'{self.default_thread_debug_level}') != -1:
            comboBoxObj.setCurrentText(f'{self.default_thread_debug_level}')

    ## Set default thread type ##
    def default_set_thread_type(self, comboBoxObj):
        for i in range(comboBoxObj.count()):
            if comboBoxObj.itemText(i).find(self.default_thread_type) != -1:
                comboBoxObj.setCurrentText(comboBoxObj.itemText(i))

    ## Matter logo click ##
    def on_label_matterlogo_clicked(self, event):
        self.option_menu_click_count += 1
        if self.option_menu_click_count >= 10:
            if self.default_config.option_menu_shown == False:
                self.menuOption.menuAction().setVisible(True)
                Log.print("Option menu OPEN in menubar")
                self.default_config.option_menu_shown = True
                QMessageBox.about(self,'Option menu','Option menu is now available.')
                self.option_menu_click_count = 0
            else:
                self.menuOption.menuAction().setVisible(False)
                Log.print("Option menu CLOSE in menubar")
                self.default_config.option_menu_shown = False
                QMessageBox.about(self,'Option menu','Option menu is closed.')
                self.option_menu_click_count = 0

    ## Create dialog ##
    def create_dialog(self, obj, cls_name):
        if obj is None:
            obj = cls_name(self)
            obj.dialog_closed.connect(self.exit_dialog)
            self.force_close.connect(obj.force_closeEvent)
            obj.show()
        else:
            Log.print("Already Opened")
        return obj

    ## Start Automation ##
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
            Log.print('No Devices are Connected/Onboarded')
            automationWindow.errorbox('No Devices are Connected/Onboarded')

    ## Emit auto onboarding state  ##
    @pyqtSlot(int, str, str)
    def auto_onboarding_state(self, state, comPort, device_num):
        Log.print(f'state {state} comport {comPort} device_num {device_num}')
        self.send_msg_about_onboarding.emit(state, comPort, device_num)

    ## Start auto onboarding ##
    def start_auto_onboarding(self):
        self.auto_onboarding = self.create_dialog(self.auto_onboarding, auto_onboardingWindow)
        self.send_msg_about_onboarding.connect(self.auto_onboarding.update_status)

    def compare_version(self):
        git_ver = Utils.get_version()
        if not git_ver:
            return
        std_ver = git_ver.split('-')[0]
        saved_std_ver = self.default_config.version.split('-')[0]
        if version.parse(std_ver) > version.parse(saved_std_ver):
            self.default_config.version = git_ver
        elif std_ver == saved_std_ver:
            x = git_ver.split('-')
            y = self.default_config.version.split('-')
            std_ver_len = len(x)
            saved_std_ver_len = len(y)
            if std_ver_len > 1 and saved_std_ver_len > 1:
                ahead = x[1]
                save_ahead = y[1]
                if ahead > save_ahead:
                     self.default_config.version = git_ver
            elif std_ver_len > 1:
                self.default_config.version = git_ver

    ## Start help ##
    def start_help(self):
        self.compare_version()
        self.help = HelpWindow(self, IOTER_NAME, self.default_config.version)
        self.help.show()

    ## Set logo ##
    def set_logo(self):
        self.labelMatterlogo.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path('ioter_logo.png'), 100, 15))
        self.labelDeviceIcon.setPixmap(Utils.get_icon_img(
            Utils.get_icon_path('devices.png'), 50, 50))

    ## Check multi bt mode ##
    def check_multi_bt_mode(self):
        if self.actionMulti_BT_mode.isChecked():
            self.default_config.multi_bt_mode = True
        else:
            self.default_config.multi_bt_mode = False
        self.default_config.save()

    ## Check start button ##
    def check_start_button(self):
        comPort = self.comboBoxCom.currentText()
        deviceNum = self.deviceManager.get_device_number()
        discriminator = self.spinBoxDiscriminator.value()

        if comPort == 'None' or len(deviceNum) == 0 or discriminator == '':
            self.pushButtonStart.setDisabled(True)
        else:
            self.pushButtonStart.setEnabled(True)

    ## Display comport in UI ##
    @pyqtSlot(str, str)
    # received msg from ioterPipe.Thread1
    def display_comport(self, action=None, path=None):
        if action == 'add':
            comPort = self.deviceManager.add_usb_device(path)
            if comPort and self.auto_onboarding:
                self.auto_onboarding.add_device(
                    comPort, self.deviceManager.get_device_vendor(comPort))
            if self.deviceManager.usb_manager.connected_phone_device():
                if self.auto_onboarding:
                    self.auto_onboarding.set_phone_connected(True)
                if not self.auto_onboarding_thread.is_running():
                    self.auto_onboarding_thread.start()
        elif action == 'remove':
            comPort = self.deviceManager.remove_usb_device(path)
            if comPort in self.dialogs:
                self.dialogs[comPort].get_window().force_closeEvent()
                if self.automation:
                    self.removed_usb.emit(
                        self.dialogs[comPort].device_info.get_device_num())
                del (self.dialogs[comPort])
            if self.auto_onboarding:
                self.auto_onboarding.remove_device(comPort)
            if not self.deviceManager.usb_manager.connected_phone_device():
                if self.auto_onboarding:
                    self.auto_onboarding.set_phone_connected(False)
                if self.auto_onboarding_thread.is_running():
                    self.auto_onboarding_thread.stop()
        comport_list = self.deviceManager.get_unused_devices()
        self.comboBoxCom.clear()
        if len(comport_list) == 0:
            self.comboBoxCom.addItem('None')
        else:
            for comport in comport_list:
                self.comboBoxCom.addItem(
                    f"{comport}/{self.deviceManager.get_device_vendor(comport)}")
        self.check_start_button()

    ## Display thread Type ##
    def display_threadType(self):
        list = os.listdir(Utils.get_thread_lib_path())
        filtered_list = [thread for thread in list if thread.startswith(
            Utils.get_thread_lib_prefix())]
        for file in filtered_list:
            self.comboBoxThread.addItem(
                file[len(Utils.get_thread_lib_prefix()):])

    ## Display device Type ##
    def display_deviceType(self):
        self.comboBoxDevice.addItems(CommandUtil.device_type_id.keys())

    ## Display ioter name ##
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
            Log.print('ioterName :' + item_data)
            return item_data
        else:
            return None

    ## Start commission ##
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

        Log.print(f"dev : {self.comboBoxCom.currentText()}")
        if self.create_device_window(deviceNum, discriminator, threadType, comPort, debugLevel, device_type):
            if self.auto_onboarding is not None:
                self.auto_onboarding.remove_device(comPort)

    ## Create device window ##
    def create_device_window(self, deviceNum, discriminator, threadType, comPort, debugLevel, device_type):
        ioterName = None

        if comPort in self.dialogs:
            Log.print(comPort + " is already in use")
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
            deviceNum, discriminator, threadType, comPort, debugLevel, ioterName,self.deviceManager,
                CommandUtil.get_device_id_by_device_type(device_type), self.auto_onboarding_thread)
        self.dialogs[comPort] = get_device_window_by_device_type(
            device_type, device_info, self.use_test_window, self.window_manager)
        if (self.dialogs[comPort] is None):
            return False

        self.dialogs[comPort].get_window(
        ).dialog_closed.connect(self.exit_dialog)
        self.dialogs[comPort].get_window().occur_abort.connect(self.reset_usb)
        self.force_close.connect(
            self.dialogs[comPort].get_window().force_closeEvent)
        self.send_msg_about_onboarding.connect(
            self.dialogs[comPort].get_window().auto_onboarding_state)
        if self.deviceManager.set_used_device(comPort, device_info) is None:
            Log.print("set_used_device is fail")
        self.display_comport()
        self.spinBoxDiscriminator.setValue((discriminator+1) & 0xFFF)
        return True

    ## Handle exit events ##
    @pyqtSlot(str)
    def exit_dialog(self, comPort):
        Log.print('exit_dialog : ' + comPort)
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
            del (self.dialogs[comPort])
            self.display_comport()
            if self.auto_onboarding:
                self.auto_onboarding.add_device(
                    comPort, self.deviceManager.get_device_vendor(comPort))
        else:
            Log.print("set_unused_device is fail")

    ## List devices used in autotest ##
    @pyqtSlot(dict)
    def autotest_used_list(self, used_device_dict):
        for device_num in used_device_dict.items():
            device_info = self.deviceManager.get_device_info_by_device_num(
                int(device_num[0]))
            comPort = device_info.get_com_port()
            self.dialogs[comPort].get_window().autotest_used(device_num[1])

    ## Reset USB devices ##
    @pyqtSlot(str)
    def reset_usb(self, comPort):
        Log.print('reset_usb :' + comPort)
        self.deviceManager.reset_device(comPort)

    ## Stop auto onboarding ##
    # must not rename closeEvent
    def closeEvent(self, event):
        # Log.print('closeEvent : ')
        re = QMessageBox.question(self, "Exit", "Do you want to exit?",
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if re == QMessageBox.Yes:
            self.usbMonitor.stop()
            self.force_close.emit(ForceClose.ALL)
            self.auto_onboarding_thread.update_onboarding_state.disconnect(self.auto_onboarding_state)
            self.auto_onboarding_thread.stop()
            event.accept()
        else:
            event.ignore()
        self.default_config.save()

    ## Hanlde key press event ##
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    ## Save current position ##
    def savePos(self):
        self.cur_pos = self.frameGeometry()

    ## Move window ##
    def winMove(self, x, y):
        fg = self.frameGeometry()
        self.winRemove(fg)
        self.window_manager.addWithPosition(
            x, y, self.frameGeometry().width(), self.frameGeometry().height())

    ## Remove window ##
    def winRemove(self, fg=None):
        if fg is None:
            fg = self.cur_pos
        self.window_manager.remove(fg.x(), fg.y(), fg.width(), fg.height())

    ## Poll move event ##
    def moveEvent(self, event):
        self.timer.start(self.polling_time_ms)

    ## Check position of window ##
    def checkPosition(self):
        if self.timer and not self.timer.isActive():
            return
        if self.frameGeometry() == self.cur_pos:
            # Window stopped to move
            self.timer.stop()
            self.winRemove()
            self.winMove(self.frameGeometry().x(), self.frameGeometry().y())
            self.savePos()
        else:
            self.winRemove()
            self.savePos()

    ## Init position timer ##
    def initPositionTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkPosition)
        self.timer.start(self.polling_time_ms)

    ## Check key Press Event ##
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F12:
            self.window_manager.showGuide()
            self.window_manager.dumpRectangles()


## stdout and stderr stream are saved to log file ##
def init_log():
    log_file_name = Utils.get_tmp_path()+datetime.now().strftime("%y%m%d-%H%M")+"-"+IOTER_NAME+".log"
    print("Log file:", log_file_name)
    lf = LogFile(open(log_file_name, "w").detach())
    sys.stderr = lf
    return Log(lf)

if __name__ == '__main__':
    # don't auto scale when drag app to a different monitor.
    # QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget {
        font-size: 15px;
        }
    ''')
    Utils.checkDir()
    ioter_log = init_log()
    screen = QDesktopWidget().availableGeometry()
    wm = window_manager.WindowManager(
        screen.x(), screen.y(), screen.width(), screen.height())
    mainWindow = MainWindow(wm)
    mainWindow.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        Log.print('Closing Window...')
    ioter_log.close()
