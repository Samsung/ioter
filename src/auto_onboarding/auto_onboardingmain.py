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
# File : auto_onboardingmain.py
# Description:
# Handles auto onboarding of devices

from auto_onboarding.auto_devicelayout import auto_device
from auto_onboarding.autod import *
from common.device_command import *
from common.device_window import *
from common.manage_device import *
from common.utils import Utils

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtTest import *
import time
import os


POWER_ON = True
POWER_OFF = False
MULTI_DEVICE = 0
SINGLE_REPEAT = 1

## Helper class ##
class help(QDialog):
    def __init__(self):
        super(help, self).__init__()
        uic.loadUi(Utils.get_view_path('helpDialog.ui'), self)
        self.setWindowTitle("Help: How to use")


## Auto-Onboarding report class ##
class report(QDialog):
    ## Init report dialog  ##
    def __init__(self):
        super(report, self).__init__()
        uic.loadUi(Utils.get_view_path('reportDialog.ui'), self)
        self.reset()
        self.btn_quit.clicked.connect(self.dlg_quit)
        self.setWindowTitle("Onboarding Report")

    ## Quit report dialog ##
    def dlg_quit(self):
        self.close()

    ## Reset stats of auto-onboarding report ##
    def reset(self):
        self.total_count = 0
        self.try_count = 0
        self.success = 0
        self.remove = 0
        self.failure = 0
        self.onboarding_failure = 0
        self.removing_failure = 0
        self.retry_remove = 0

    ## Print results of auto-onboarding ##
    def printResult(self):
        print(f"Total count   : {self.total_count}")
        print(f"Success       : {self.success}")
        print(f"- Onboarding  : {self.success}")
        print(f"- Removing    : {self.remove}")
        print(f"Failure       : {self.failure}")
        print(f"- Onboarding  : {self.onboarding_failure}")
        print(f"- Removing    : {self.removing_failure}")
        self.lbl_total_count.setText(str(self.total_count))
        self.lbl_success.setText(str(self.success))
        self.lbl_onboarding_success.setText(str(self.success))
        self.lbl_removing_success.setText(str(self.remove))
        self.lbl_failure.setText(str(self.failure))
        self.lbl_onboarding_failure.setText(str(self.onboarding_failure))
        self.lbl_removing_failure.setText(str(self.removing_failure))
        self.show()


## Main Window of auto-onboarding class ##
class auto_onboardingWindow(QMainWindow):
    dialog_closed = pyqtSignal(str)

    ## Init auto_onboardingWindow ##
    def __init__(self, parent):
        super(auto_onboardingWindow, self).__init__()
        self.parent = parent
        self.axis_y = 3
        self.width = 0
        self.objs = []
        self.order = []
        self.report = report()
        self.test_category = MULTI_DEVICE
        self.force_quit = False
        uic.loadUi(Utils.get_view_path("auto_onboardingWindow.ui"), self)
        self.setWindowTitle("Auto onboarding")
        self.chkbox_all.stateChanged.connect(self.toggle_chkbox_all)
        self.btn_onboard.clicked.connect(self.auto_multi_onboarding)
        self.btn_repeat_test.clicked.connect(self.auto_single_repeat)
        self.btn_remove.clicked.connect(self.auto_multi_removing)
        self.actionHow_to_use.triggered.connect(self.how_to_use)
        self.default_discriminator.valueChanged.connect(
            self.update_discriminator)
        self.default_device_type.activated[str].connect(
            self.update_device_type)
        self.default_thread_type.activated[str].connect(
            self.update_thread_type)
        self.default_debug_level.activated[str].connect(
            self.update_debug_level)
        self.add(self.parent.deviceManager)
        self.init_ui_setting()
        QCoreApplication.processEvents()
        self.progressBar.setValue(0)
        self.onboarding_style_sheet = """
        QProgressBar {
            font-weight: bold;
        }
        QProgressBar::chunk {
            background-color: #69F0AE;
            width: 10px; 
            margin: 0.5px;
        }
        """
        self.remove_style_sheet = """
        QProgressBar {
            font-weight: bold;
        }
        QProgressBar::chunk {
            background-color: #FF8A80;
            width: 10px; 
            margin: 0.5px;
        }
        """
        self.repeat_style_sheet = """
        QProgressBar {
            font-weight: bold;
        }
        QProgressBar::chunk {
            background-color: #40C4FF;
            width: 10px; 
            margin: 0.5px;
        }
        """
        self.total_process = 0
        self.current_process = 0
        self.onboarding_state = 0
        self.progressBar.setStyleSheet(self.onboarding_style_sheet)
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Select devices and button", self)
        self.status_bar.addPermanentWidget(self.status_label)

    ## Toggle all check boxes ##
    def toggle_chkbox_all(self):
        if self.chkbox_all.isChecked():
            for i in range(len(self.objs)):
                if not self.objs[i].chkbox.isChecked():
                    self.objs[i].chkbox.toggle()
        else:
            for i in range(len(self.objs)):
                if self.objs[i].chkbox.isChecked():
                    self.objs[i].chkbox.toggle()

    ## Init UI settings ##
    def init_ui_setting(self):
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setEnabled(True)
        self.scrollAreaWidgetContents.setMinimumSize(QSize(1, 1))
        self.chkbox_all.setMinimumWidth(15)
        self.chkbox_all.setMaximumWidth(15)
        self.lbl_comport.setMinimumWidth(125)
        self.lbl_comport.setMaximumWidth(125)
        self.default_device_type.setMinimumWidth(
            self.objs[0].combo_device_type.width())
        self.default_device_type.setMaximumWidth(
            self.objs[0].combo_device_type.width())
        self.default_thread_type.setMinimumWidth(
            self.objs[0].combo_thread_type.width())
        self.default_thread_type.setMaximumWidth(
            self.objs[0].combo_thread_type.width())
        self.default_debug_level.setMinimumWidth(
            self.objs[0].combo_debug_level.width())
        self.default_debug_level.setMaximumWidth(
            self.objs[0].combo_debug_level.width())
        self.default_discriminator.setMinimumWidth(
            self.objs[0].discriminator.width())
        self.default_discriminator.setMaximumWidth(
            self.objs[0].discriminator.width())
        self.default_device_type.setMinimumWidth(
            self.objs[0].combo_device_type.width())
        self.default_device_type.setMaximumWidth(
            self.objs[0].combo_device_type.width())
        self.default_thread_type.setMinimumWidth(
            self.default_thread_type.width())
        self.default_thread_type.setMaximumWidth(
            self.default_thread_type.width())
        self.default_debug_level.setMinimumWidth(
            self.default_debug_level.width())
        self.default_debug_level.setMaximumWidth(
            self.default_debug_level.width())
        self.default_discriminator.setMinimumWidth(
            self.default_discriminator.width())
        self.default_discriminator.setMaximumWidth(
            self.default_discriminator.width())
        self.default_discriminator.setRange(1000, 9999)
        self.default_discriminator.setValue(
            self.parent.spinBoxDiscriminator.value())
        self.default_discriminator.setToolTip('Discriminator')
        self.default_discriminator.setToolTipDuration(0)
        self.default_device_type.addItem("Device-Type")
        self.default_device_type.addItems(CommandUtil.device_type_id.keys())
        self.default_thread_type.addItem("Thread-Type")
        self.default_thread_type.addItems(self.get_thread_type_list())
        self.default_debug_level.addItem("Log")
        self.default_debug_level.addItems(["1", "2", "3", "4", "5"])
        self.setFixedWidth(700)

    ## Update discriminator values used during auto-onboarding ##
    def update_discriminator(self):
        for i in range(len(self.objs)):
            self.objs[i].discriminator.setValue(
                self.default_discriminator.value() + i)

    ## Update device types ##
    def update_device_type(self, selected):
        if selected != "Device-Type":
            for i in range(len(self.objs)):
                self.objs[i].combo_device_type.setCurrentText(selected)
        self.default_device_type.setCurrentIndex(0)

    ## Update thread types ##
    def update_thread_type(self, selected):
        if selected != "Thread-Type":
            for i in range(len(self.objs)):
                self.objs[i].combo_thread_type.setCurrentText(selected)
        self.default_thread_type.setCurrentIndex(0)

    ## Update debug level ##
    def update_debug_level(self, selected):
        if selected != "Log":
            for i in range(len(self.objs)):
                self.objs[i].combo_debug_level.setCurrentText(selected)
        self.default_debug_level.setCurrentIndex(0)

    ## Get thread types list ##
    def get_thread_type_list(self):
        version = []
        list = os.listdir(Utils.get_thread_lib_path())
        filtered_list = [thread for thread in list if thread.startswith(
            Utils.get_thread_lib_prefix())]
        for file in filtered_list:
            version.append(file[len(Utils.get_thread_lib_prefix()):])
        return version

    ## Help dialog ##
    def how_to_use(self):
        self.helpDlg = help()
        self.helpDlg.show()

    ## Add devices to list ##
    def add(self, dm):
        self.clear()
        unused_vendor_list = dict()
        unused_device_list = dm.get_unused_devices()
        for comport in unused_device_list:
            unused_vendor_list[comport] = dm.get_device_vendor(comport)
            self.add_device(comport, unused_vendor_list[comport])
        self.show()

    ## Add device ##
    def add_device(self, comport, vendor):
        for i in range(len(self.objs)):
            if self.objs[i].comport == comport:
                return
        self.objs.append(auto_device())
        index = len(self.objs) - 1
        self.objs[index].setupUi(self, comport, vendor)
        self.objs[index].index = index
        self.objs[index].discriminator.setValue(3840+index)
        self.parent.default_set_thread_type(self.objs[index].combo_thread_type)
        self.parent.default_set_thread_debug_level(self.objs[index].combo_debug_level)
        self.update()
        self.objs[index].layoutWidget.show()
        self.adjust_geometry()
        self.scrollAreaWidgetContents.setMinimumSize(
            QSize(self.axis_y, self.axis_y))

    ## Remove device ##
    def remove_device(self, comPort):
        index = self.get_index_from_comport(comPort)
        if index is not None:
            self.objs[index].layoutWidget.hide()
            del self.objs[index]
            self.update()
            self.adjust_geometry()
            self.scrollAreaWidgetContents.setMinimumSize(
                QSize(self.axis_y, self.axis_y))

    ## Device power on/off ##
    def device_powerOnOff(self, comport, Onoff):
        if comport not in self.parent.dialog:
            return
        if Onoff:  # power on
            if not self.parent.dialog[comport].get_window().pushButtonDevicePower.isChecked():
                self.parent.dialog[comport].get_window(
                ).pushButtonDevicePower.toggle()
        else:
            if self.parent.dialog[comport].get_window().pushButtonDevicePower.isChecked():
                self.parent.dialog[comport].get_window(
                ).pushButtonDevicePower.toggle()

    ## Auto multiple onboarding ##
    def auto_multi_onboarding(self):
        self.test_category = MULTI_DEVICE
        self.order.clear()
        checked = False
        self.total_process = 0
        self.current_process = 0
        self.progressBar.setStyleSheet(self.onboarding_style_sheet)
        self.status_label.setText("auto_onboarding")
        for i in range(len(self.objs)):
            if self.objs[i].chkbox.isChecked():
                checked = True
                if self.objs[i].comport in self.parent.dialog:
                    print(
                        f"{self.objs[i].comport} / Device {self.parent.dialog[self.objs[i].comport].device_info.device_num} is already used")
                    continue
                self.order.insert(0, self.objs[i].comport)
                self.total_process += 1
                self.load_device_window(i)
                QTest.qWait(200)
        if checked:
            try:
                comport = self.order.pop()
                self.device_powerOnOff(comport, POWER_ON)
                self.status_bar.showMessage("Onboarding... " + str(comport))
                self.update_progress_label()
            except IndexError:
                err = simpleDlg("No device is selected",
                                "Check the device for onboarding")
                print("Error: No device is selected for onboarding.")
        else:
            err = simpleDlg("No device is selected",
                            "Check the device for onboarding")
            print("Error: No device is selected for onboarding.")

    ## Auto multiple remove ##
    def auto_multi_removing(self):
        self.test_category = MULTI_DEVICE
        self.order.clear()
        checked = False
        self.total_process = 0
        self.current_process = 0
        self.progressBar.setStyleSheet(self.remove_style_sheet)
        self.status_label.setText("auto_removing")
        for i in range(len(self.objs)):
            if self.objs[i].chkbox.isChecked():
                if not self.objs[i].comport in self.parent.dialog:
                    print(f"{self.objs[i].comport} is not onboarded")
                    continue
                checked = True
                self.order.insert(0, self.objs[i].comport)
                self.total_process += 1
                self.update_progress_label()
        if checked:
            try:
                comport = self.order.pop()
                self.device_powerOnOff(comport, POWER_OFF)
                self.status_bar.showMessage("Removing... " + str(comport))
                self.update_progress_label()
            except IndexError:
                err = simpleDlg("No device is selected",
                                "Check the device for removing")
                print("Error: No device is selected for removing.")
        else:
            err = simpleDlg("No device is selected",
                            "Check the device for removing")
            print("Error: No device is selected for removing..")

    ## Single device can use Auto onboarding repeat test ##
    def auto_single_repeat(self):
        self.test_category = SINGLE_REPEAT
        onlyOne = 0
        checkedIndex = 0
        self.total_process = 0
        self.current_process = 0
        self.progressBar.setStyleSheet(self.repeat_style_sheet)
        self.status_label.setText("repeat_onboarding")
        for i in range(len(self.objs)):
            if self.objs[i].chkbox.isChecked():
                onlyOne += 1
                checkedIndex = i
        if onlyOne == 1:
            self.report.reset()
            self.report.total_count = self.repeat.value()
            self.total_process = self.repeat.value()
            self.update_progress_label()
            self.load_device_window(checkedIndex)
            comport = self.objs[checkedIndex].comport
            self.status_bar.showMessage(f"{self.current_process+1}th try...")
            self.report.try_count += 1
            print(f"{self.report.try_count}th try...")
            self.device_powerOnOff(comport, POWER_ON)
        else:
            err = simpleDlg(
                "Wrong input", "Only one device can use Auto onboarding repeat test!!")
            print("only one device can use Auto onboarding repeat test!!")
            return

    ## Progress label update ##
    def update_progress_label(self):
        if self.total_process > self.current_process :
            status_text = f"{self.current_process} / {self.total_process}"
        else:
            status_text = "Complete"
        self.progressBar.setFormat(status_text)
        self.progressBar.setValue(int((self.current_process/self.total_process)*100))

    ## Load device window ##
    def load_device_window(self, i):
        deviceNum = str(self.parent.deviceManager.get_device_number()[0])
        discriminator = self.objs[i].discriminator.value()
        threadType = self.objs[i].combo_thread_type.currentText()
        comPort = self.objs[i].comport  # usb_device_label.text().split('/')[0]
        debugLevel = self.objs[i].combo_debug_level.currentText()
        device_type = self.objs[i].combo_device_type.currentText()
        self.objs[i].device_name = f'{device_type}-{deviceNum}'

        print(f'load_device_window comPort {comPort}')
        if self.parent.create_device_window(deviceNum, discriminator, threadType, comPort, debugLevel, device_type):
            if not self.parent.dialog[comPort].get_window().chkbox_auto.isChecked():
                self.parent.dialog[comPort].get_window().chkbox_auto.toggle()

    ## multi device onboarding process ##
    def multi_device_process(self, index, value, comport, device_num):
        self.current_process += 1
        self.update_progress_label()
        # onboarding
        if value == STOnboardingResult.ONBOARDING_SUCCESS:  # success
            self.objs[index].status.setText(self.objs[index].device_name)
            self.status_bar.showMessage("Onboarding success " + str(comport))
        elif value == STOnboardingResult.ONBOARDING_FAILURE:  # failed
            if comport in self.parent.dialog:
                self.parent.dialog[comport].get_window().force_closeEvent()
            self.objs[index].status.setText("failed")
            self.status_bar.showMessage("Onboarding failed " + str(comport))
        # removing
        elif value == STOnboardingResult.REMOVING_SUCCESS:  # success
            self.objs[index].status.setText("ready")
            self.status_bar.showMessage("Removing success " + str(comport))
        elif value == STOnboardingResult.REMOVING_FAILURE:  # failed
            self.objs[index].status.setText(self.objs[index].device_name)
            self.status_bar.showMessage("Removing failed " + str(comport))
        QCoreApplication.processEvents()
        time.sleep(1)
        if len(self.order) > 0 and value < 2:  # keep proceed multi onboarding
            next = self.order.pop()
            self.device_powerOnOff(next, POWER_ON)
            self.status_bar.showMessage("Onboarding... " + str(next))
        elif value >= 2:  # keep proceed multi removing
            if comport in self.parent.dialog:
                self.parent.dialog[comport].get_window().force_closeEvent()
            if len(self.order) > 0:
                next = self.order.pop()
                self.device_powerOnOff(next, POWER_OFF)
                self.status_bar.showMessage("Removing... " + str(next))

    ## Single device onboarding process ##
    def single_repeat_process(self, index, value, comport, device_num):
        # onboarding
        if value == STOnboardingResult.ONBOARDING_SUCCESS:  # success
            self.objs[index].status.setText(self.objs[index].device_name)
            self.status_bar.showMessage(f"{self.current_process+1}th try onboarding success ")
            self.report.success += 1
            # time.sleep(3)
            QCoreApplication.processEvents()
            self.device_powerOnOff(comport, POWER_OFF)
            # self.parent.dialog[comport].get_window().auto_remove()
        elif value == STOnboardingResult.ONBOARDING_FAILURE:  # failed
            self.objs[index].status.setText("failed")
            self.current_process += 1
            self.status_bar.showMessage(f"{self.current_process}th try onboarding failed")
            self.report.onboarding_failure += 1
            self.report.failure += 1
            self.report.try_count += 1
            print(
                f"{self.report.onboarding_failure} onboarding failed.. \n{self.report.try_count}th try...")
            if comport in self.parent.dialog:
                self.parent.dialog[comport].get_window().force_closeEvent()
            QTest.qWait(5000)
            self.load_device_window(index)
            # time.sleep(1)
            QCoreApplication.processEvents()
            self.device_powerOnOff(comport, POWER_ON)
        # removing
        elif value == STOnboardingResult.REMOVING_SUCCESS:  # success
            self.objs[index].status.setText("ready")
            self.status_bar.showMessage(f"{self.current_process+1}th try removing success")
            if comport in self.parent.dialog:
                self.parent.dialog[comport].get_window().force_closeEvent()
            self.report.remove += 1
            self.current_process += 1
            # self.report.try_count += 1
            if self.report.try_count >= self.report.total_count:
                self.report.printResult()
                return
            self.report.try_count += 1
            print(f"{self.report.try_count}th try...")
            QTest.qWait(5000)
            self.load_device_window(index)
            # time.sleep(1)
            QCoreApplication.processEvents()
            self.device_powerOnOff(comport, POWER_ON)
        elif value == STOnboardingResult.REMOVING_FAILURE:  # failed
            self.objs[index].status.setText(self.objs[index].device_name)
            self.status_bar.showMessage(f"{self.current_process+1}th try removing failed")
            self.report.retry_remove += 1
            self.current_process += 1
            if (self.report.retry_remove >= 3):  # ignore removing failure and proceed next step
                self.report.retry_remove = 0
                self.report.removing_failure += 1
                # self.report.try_count += 1
                if comport in self.parent.dialog:
                    self.parent.dialog[comport].get_window().force_closeEvent()
                # self.parent.dialog[comport].get_window().dialog_closed.emit(self.parent.dialog[comport].get_window().device_info.com_port)
                if self.report.try_count > self.report.total_count:
                    self.report.printResult()
                    return
                self.report.try_count += 1
                # removing failed.. but still remain next onboarding test. keep going.
                print(f"{self.report.try_count}th try...")
                QTest.qWait(5000)
                self.load_device_window(index)
                self.device_powerOnOff(comport, POWER_ON)
            else:
                if comport in self.parent.dialog:
                    self.parent.dialog[comport].get_window().auto_remove()
        
        self.update_progress_label()
        self.status_bar.showMessage(f"{self.current_process+1}th try...")

    ## Update status ##
    @pyqtSlot(int, str, str)
    def update_status(self, value, comport, device_num):
        if self.force_quit:
            return
        index = self.get_index_from_comport(comport)
        if index is not None:
            # multi
            if self.test_category == MULTI_DEVICE:
                self.multi_device_process(index, value, comport, device_num)
            # single (repeat)
            elif self.test_category == SINGLE_REPEAT:
                self.single_repeat_process(index, value, comport, device_num)
            self.update_progress_label()

    ## Get index from comport ##
    def get_index_from_comport(self, comport):
        for i in range(len(self.objs)):
            if self.objs[i].comport == comport:
                return i
        return None

    ## clear ##
    def clear(self):
        diff = (len(self.objs)-1) - 0 + 1
        while (diff):
            try:
                if self.objs[0]:
                    self.objs[0].layoutWidget.deleteLater()
                    del self.objs[0]
                    diff -= 1
                    self.axis_y -= 30
            except Exception as e:
                print(e)
        self.adjust_geometry()
        self.scrollAreaWidgetContents.setMinimumSize(
            QSize(self.axis_y, self.axis_y))

    ## Adjust geometry ##
    def adjust_geometry(self):
        axis_y = 0
        for x in range(len(self.objs)):
            try:
                if self.objs[x]:
                    self.objs[x].index = x
                    self.objs[x].layoutWidget.move(0, axis_y)
                    axis_y += 30
            except Exception as e:
                print(x, e)
        self.scrollAreaWidgetContents.setMinimumSize(
            QSize(self.axis_y, self.axis_y))

    ## Resize Event ##
    def resizeEvent(self, event):
        self.width = self.size().width()
        for x in range(len(self.objs)):
            self.objs[x].layoutWidget.resize(self.width-20, 29)
        QMainWindow.resizeEvent(self, event)

    ## Close Auto onboarding ##
    def closeEvent(self, event):
        if not self.force_quit:
            re = QMessageBox.question(self, "Exit", "Do you want to close Auto onboarding and all device windows as well?",
                                      QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
            if re == QMessageBox.Yes:
                self.dialog_closed.emit("auto_onboarding_all")
                event.accept()
            elif re == QMessageBox.No:
                self.dialog_closed.emit("auto_onboarding")
                event.accept()
            elif re == QMessageBox.Cancel:
                event.ignore()

    ## Quit Auto Onboarding ##
    def force_closeEvent(self, device):
        if (device & ForceClose.AUTO_ONBOARDING) and not self.force_quit:
            print('quit Auto Onboarding')
            self.force_quit = True
            self.close()
