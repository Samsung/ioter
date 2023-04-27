from auto_onboarding.auto_devicelayout import auto_device
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


MULTI_DEVICE = 0
SINGLE_REPEAT = 1
ONBOARDING_SUCCESS = 1
ONBOARDING_FAILURE = 0
REMOVING_SUCCESS = 3
REMOVING_FAILURE = 2


class simpleDlg(QDialog):
    def __init__(self, title, content):
        super(simpleDlg, self).__init__()
        self.app = QErrorMessage()
        self.app.showMessage(content)
        self.app.setWindowModality(Qt.WindowModal)
        self.app.setWindowTitle(title)
        self.app.exec()


class help(QDialog):
    def __init__(self):
        super(help, self).__init__()
        uic.loadUi(Utils.get_view_path('helpDialog.ui'), self)
        self.setWindowTitle("Help: How to use")


class report(QDialog):
    def __init__(self):
        super(report, self).__init__()
        uic.loadUi(Utils.get_view_path('reportDialog.ui'), self)
        self.reset()
        self.btn_quit.clicked.connect(self.dlg_quit)
        self.setWindowTitle("Onboarding Report")

    def dlg_quit(self):
        self.close()

    def reset(self):
        self.total_count = 0
        self.try_count = 0
        self.success = 0
        self.remove = 0
        self.failure = 0
        self.onboarding_failure = 0
        self.removing_failure = 0
        self.retry_remove = 0

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


class auto_onboardingWindow(QMainWindow):
    dialog_closed = pyqtSignal(str)

    def __init__(self, parent):
        super(auto_onboardingWindow, self).__init__()
        self.parent = parent
        self.axis_y = 3
        self.width = 0
        self.objs = []
        self.order = []
        self.report = report()
        self.test_category = MULTI_DEVICE
        self.force_close_flag = False
        self.device_name = []
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

    def toggle_chkbox_all(self):
        if self.chkbox_all.isChecked():
            for i in range(len(self.objs)):
                if not self.objs[i].chkbox.isChecked():
                    self.objs[i].chkbox.toggle()
        else:
            for i in range(len(self.objs)):
                if self.objs[i].chkbox.isChecked():
                    self.objs[i].chkbox.toggle()

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

    def update_discriminator(self):
        for i in range(len(self.objs)):
            self.objs[i].discriminator.setValue(
                self.default_discriminator.value() + i)

    def update_device_type(self, selected):
        if selected != "Device-Type":
            for i in range(len(self.objs)):
                self.objs[i].combo_device_type.setCurrentText(selected)
        self.default_device_type.setCurrentIndex(0)

    def update_thread_type(self, selected):
        if selected != "Thread-Type":
            for i in range(len(self.objs)):
                self.objs[i].combo_thread_type.setCurrentText(selected)
        self.default_thread_type.setCurrentIndex(0)

    def update_debug_level(self, selected):
        if selected != "Log":
            for i in range(len(self.objs)):
                self.objs[i].combo_debug_level.setCurrentText(selected)
        self.default_debug_level.setCurrentIndex(0)

    def get_thread_type_list(self):
        version = []
        list = os.listdir(Utils.get_thread_lib_path())
        filtered_list = [thread for thread in list if thread.startswith(
            Utils.get_thread_lib_prefix())]
        for file in filtered_list:
            version.append(file[len(Utils.get_thread_lib_prefix()):])
        return version

    def how_to_use(self):
        self.helpDlg = help()
        self.helpDlg.show()

    def add(self, dm):
        self.clear()
        unused_vendor_list = dict()
        unused_device_list = dm.get_unused_devices()
        for comport in unused_device_list:
            unused_vendor_list[comport] = dm.get_device_vendor(comport)
            self.add_device(comport, unused_vendor_list[comport])
        self.show()

    def add_device(self, comport, vendor):
        for i in range(len(self.objs)):
            if self.objs[i].comport == comport:
                return
        self.objs.append(auto_device())
        index = len(self.objs) - 1
        self.objs[index].setupUi(self, comport, vendor)
        self.objs[index].index = index
        self.objs[index].discriminator.setValue(3840+index)
        self.update()
        self.objs[index].layoutWidget.show()
        self.adjust_geometry()
        self.scrollAreaWidgetContents.setMinimumSize(
            QSize(self.axis_y, self.axis_y))

    def remove_device(self, comPort):
        for i in range(len(self.objs)):
            # print(str(i) + " comport : " + self.objs[i].comport)
            if self.objs[i].comport == comPort:
                self.objs[i].layoutWidget.hide()
                del self.objs[i]
                self.update()
                self.adjust_geometry()
                self.scrollAreaWidgetContents.setMinimumSize(
                    QSize(self.axis_y, self.axis_y))
                return

    def auto_multi_onboarding(self):
        self.test_category = MULTI_DEVICE
        self.order.clear()
        checked = False
        for i in range(len(self.objs)):
            if self.objs[i].chkbox.isChecked():
                checked = True
                if self.objs[i].comport in self.parent.dialog:
                    print(
                        f"{self.objs[i].comport} / Device {self.parent.dialog[self.objs[i].comport].device_info.device_num} is already used")
                    continue
                self.order.insert(0, self.objs[i].comport)
                self.load_device_window(i)
        if checked:
            try:
                comport = self.order.pop()
                if comport in self.parent.dialog:
                    if not self.parent.dialog[comport].get_window().pushButtonDevicePower.isChecked():
                        self.parent.dialog[comport].get_window(
                        ).pushButtonDevicePower.toggle()
            except IndexError:
                err = simpleDlg("No device is selected",
                                "Check the device for onboarding")
                print("Error: No device is selected for onboarding.")
        else:
            err = simpleDlg("No device is selected",
                            "Check the device for onboarding")
            print("Error: No device is selected for onboarding.")

    def auto_multi_removing(self):
        self.test_category = MULTI_DEVICE
        self.order.clear()
        checked = False
        for i in range(len(self.objs)):
            if self.objs[i].chkbox.isChecked():
                if not self.objs[i].comport in self.parent.dialog:
                    print(f"{self.objs[i].comport} is not onboarded")
                    continue
                checked = True
                self.order.insert(0, self.objs[i].comport)
        if checked:
            try:
                comport = self.order.pop()
                if comport in self.parent.dialog:
                    if self.parent.dialog[comport].get_window().pushButtonDevicePower.isChecked():
                        self.parent.dialog[comport].get_window(
                        ).pushButtonDevicePower.toggle()
            except IndexError:
                err = simpleDlg("No device is selected",
                                "Check the device for removing")
                print("Error: No device is selected for removing.")
        else:
            err = simpleDlg("No device is selected",
                            "Check the device for removing")
            print("Error: No device is selected for removing..")

    def auto_single_repeat(self):
        self.test_category = SINGLE_REPEAT
        onlyOne = 0
        checkedIndex = 0
        for i in range(len(self.objs)):
            if self.objs[i].chkbox.isChecked():
                onlyOne += 1
                checkedIndex = i
        if onlyOne == 1:
            self.report.reset()
            self.report.total_count = self.repeat.value()
            self.load_device_window(checkedIndex)
            comport = self.objs[checkedIndex].comport
            self.report.try_count += 1
            print(f"{self.report.try_count}th try...")
            if comport in self.parent.dialog:
                if not self.parent.dialog[comport].get_window().pushButtonDevicePower.isChecked():
                    self.parent.dialog[comport].get_window(
                    ).pushButtonDevicePower.toggle()
        else:
            err = simpleDlg(
                "Wrong input", "Only one device can use Auto onboarding repeat test!!")
            print("only one device can use Auto onboarding repeat test!!")
            return

    def load_device_window(self, i):
        deviceNum = str(self.parent.deviceManager.get_device_number()[0])
        discriminator = self.objs[i].discriminator.value()
        threadType = self.objs[i].combo_thread_type.currentText()
        comPort = self.objs[i].comport  # usb_device_label.text().split('/')[0]
        debugLevel = self.objs[i].combo_debug_level.currentText()
        device_type = self.objs[i].combo_device_type.currentText()
        self.device_name.insert(i, f'{device_type}-{deviceNum}')

        if self.parent.create_device_window(deviceNum, discriminator, threadType, comPort, debugLevel, device_type):
            if not self.parent.dialog[comPort].get_window().chkbox_auto.isChecked():
                self.parent.dialog[comPort].get_window().chkbox_auto.toggle()

    def multi_device_process(self, index, value, comport, device_num):
        # onboarding
        if value == ONBOARDING_SUCCESS:  # success
            self.objs[index].status.setText(f'{self.device_name[index]}')
        elif value == ONBOARDING_FAILURE:  # failed
            self.parent.dialog[comport].get_window().force_closeEvent()
            self.objs[index].status.setText("failed")
        # removing
        elif value == REMOVING_SUCCESS:  # success
            self.objs[index].status.setText("ready")
        elif value == REMOVING_FAILURE:  # failed
            self.objs[index].status.setText(f'{self.device_name[index]}')
        QCoreApplication.processEvents()
        time.sleep(1)
        if len(self.order) > 0 and value < 2:  # keep proceed multi onboarding
            next = self.order.pop()
            if next in self.parent.dialog:
                if not self.parent.dialog[next].get_window().pushButtonDevicePower.isChecked():
                    self.parent.dialog[next].get_window(
                    ).pushButtonDevicePower.toggle()
        elif len(self.order) > 0 and value >= 2:  # keep proceed multi removing
            self.parent.dialog[comport].get_window().force_closeEvent()
            next = self.order.pop()
            if next in self.parent.dialog:
                if self.parent.dialog[next].get_window().pushButtonDevicePower.isChecked():
                    self.parent.dialog[next].get_window(
                    ).pushButtonDevicePower.toggle()
        elif value >= 2:  # keep proceed multi removing
            if comport in self.parent.dialog:
                self.parent.dialog[comport].get_window().force_closeEvent()

    def single_repeat_process(self, index, value, comport, device_num):
        # onboarding
        if value == ONBOARDING_SUCCESS:  # success
            self.objs[index].status.setText(f'{self.device_name[index]}')
            self.report.success += 1
            # time.sleep(3)
            QCoreApplication.processEvents()
            if comport in self.parent.dialog:
                if self.parent.dialog[comport].get_window().pushButtonDevicePower.isChecked():
                    self.parent.dialog[comport].get_window(
                    ).pushButtonDevicePower.toggle()
            # self.parent.dialog[comport].get_window().auto_remove()
        elif value == ONBOARDING_FAILURE:  # failed
            self.objs[index].status.setText("failed")
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
            if comport in self.parent.dialog:
                if not self.parent.dialog[comport].get_window().pushButtonDevicePower.isChecked():
                    self.parent.dialog[comport].get_window(
                    ).pushButtonDevicePower.toggle()
        # removing
        elif value == REMOVING_SUCCESS:  # success
            self.objs[index].status.setText("ready")
            if comport in self.parent.dialog:
                self.parent.dialog[comport].get_window().force_closeEvent()
            self.report.remove += 1
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
            if comport in self.parent.dialog:
                if not self.parent.dialog[comport].get_window().pushButtonDevicePower.isChecked():
                    self.parent.dialog[comport].get_window(
                    ).pushButtonDevicePower.toggle()
        elif value == REMOVING_FAILURE:  # failed
            self.objs[index].status.setText(f'{self.device_name[index]}')
            self.report.retry_remove += 1
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
                if comport in self.parent.dialog:
                    if not self.parent.dialog[comport].get_window().pushButtonDevicePower.isChecked():
                        self.parent.dialog[comport].get_window(
                        ).pushButtonDevicePower.toggle()
            else:
                if comport in self.parent.dialog:
                    self.parent.dialog[comport].get_window().auto_remove()

    @pyqtSlot(int, str, str)
    def update_status(self, value, comport, device_num):
        index = self.get_index_from_comport(comport)
        # multi
        if self.test_category == MULTI_DEVICE:
            self.multi_device_process(index, value, comport, device_num)
        # single (repeat)
        elif self.test_category == SINGLE_REPEAT:
            self.single_repeat_process(index, value, comport, device_num)

    def get_index_from_comport(self, comport):
        for i in range(len(self.objs)):
            if self.objs[i].comport == comport:
                return i

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

    def resizeEvent(self, event):
        self.width = self.size().width()
        for x in range(len(self.objs)):
            self.objs[x].layoutWidget.resize(self.width-20, 29)
        QMainWindow.resizeEvent(self, event)

    def closeEvent(self, event):
        if not self.force_close_flag:
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

    def force_closeEvent(self):
        print('quit Auto Onboarding')
        self.force_close_flag = True
        self.close()
