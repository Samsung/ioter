
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
# File : automationmain.py
# Description:
# Handle Automation Window.

from automation.looplayout import Ui_Loop
from automation.devicelayout import Ui_Device
from automation.insertdialogbox import InsertDialog
from automation.filedialog import FileDialog
from automation.ProcessCmd import *
from automation.logtrackscriptcntl import *
from common.utils import Utils
from common.device_command import *
import os
import xml.etree.ElementTree as Etree
from datetime import datetime
from PyQt5 import QtWidgets, uic, QtCore

class automationWindow(QtWidgets.QMainWindow):
    dialog_closed = QtCore.pyqtSignal(str)
    send_used_list = QtCore.pyqtSignal(dict)

    ## Set Up Automation window ##
    def __init__(self, parent):
        super(automationWindow, self).__init__()
        self.parent = parent
        self.objs = []
        self.use_test_window = parent.use_test_window
        self.width = 0
        self.axis_y = 3
        self.curcmd = 0
        self.totalcmd = -1
        self.old_highlight = -1
        self.dialog = None
        self.autotestThread = 0
        self.autotestComplete = False
        self.logtrack = 0
        self.force_quit = False
        self.currentOpenFile = None
        self.devMgrObj = parent.deviceManager
        self.commandList = dict()
        uic.loadUi(Utils.get_view_path('automationwindow.ui'), self)
        self.resize(600, 700)
        self.setWindowTitle('Automation')
        self.btn_LoopStartEnd.clicked.connect(self.addLoopStartEnd)
        self.btn_Devicecommand.clicked.connect(lambda: self.addDev(-1))
        self.btn_Sleep.clicked.connect(lambda: self.addSleep(-1))
        self.Clearlog_btn.setStyleSheet(
            'background-color: rgb(98, 160, 234);font-weight: bold;font: 16pt;font-weight: bold;')
        self.Clearlog_btn.clicked.connect(self.clear_log_window)
        self.logwindow_output.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOn)
        self.logwindow_output.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.logwindow_output.verticalScrollBar().rangeChanged.connect(self.scrollToBottom,)
        self.logwindow_output.setReadOnly(True)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.resizeEvent = self.resizeEvent
        self.scrollArea.resize(482, 537)
        self.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(1, 1))
        self.btn_Run.setCheckable(True)
        self.btn_Run.toggled.connect(self.run)
        self.btn_Clearall.clicked.connect(
            lambda: self.clear(0, len(self.objs)-1))
        self.actionOpen.setShortcut("Ctrl+O")
        self.actionSave.setShortcut("Ctrl+S")
        self.actionExit.setShortcut("Ctrl+X")
        self.actionOpen.triggered.connect(self.openfile)
        self.actionSave.triggered.connect(lambda: self.savefile(0))
        self.actionExit.triggered.connect(self.close)
        self.testprogressBar.setMinimum(0)
        self.show()
        self.loadCommandList()

    ## Load Commands ##
    def loadCommandList(self):
        for device in self.devMgrObj.get_used_devices():
            if device.get_commissioning_state():
                self.commandList[device.device_num] = self.parent.dialog[device.com_port]._return_command()

    ## Handle scroll bar to bootom##
    def scrollToBottom(self, minVal=None, maxVal=None):
        self.scrollArea.verticalScrollBar().setValue(
            self.scrollArea.verticalScrollBar().maximum())

    ## Clear Log window ##
    def clear_log_window(self):
        if not self.autotestThread:
            self.logwindow_output.clear()
            self.testprogressBar.setValue(0)

    ## Close/Exit Event Handler ##
    def closeEvent(self, event):
        if not self.force_quit:
            re = QtWidgets.QMessageBox.question(self, "Exit", "Do you want to exit from Automation?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
            if re == QtWidgets.QMessageBox.Yes:
                self.force_closeEvent(ForceClose.AUTOMATION)
                self.dialog_closed.emit("Automation")
                event.accept()
            else:
                event.ignore()

    ## Log window ##
    def logwindow(self, string):
        self.logwindow_output.insertPlainText(
            "["+str(datetime.now().strftime('%Y-%m-%d-%H:%M'))+"]: "+string+'\n\n')

    ## Open File Event Handler ##
    def openfile(self):
        openfile = FileDialog()
        openfile.openFileNameDialog()
        openfile.show()
        if openfile.fileName:
            self.load(openfile.fileName)
            self.logwindow('File loaded :  "' +
                           str(openfile.fileName) + '" Successfully')
            self.testprogressBar.setValue(0)
        openfile.close()

    ## Save File Event Handler ##
    def savefile(self, valid):
        if valid == 0:  # Check if already validated
            if not self.validatefield():
                print('Validation Failed')
                return False
        savefile = FileDialog()
        savefile.saveFileDialog()
        savefile.show()
        if savefile.fileName:
            self.save(savefile.fileName)
            self.logwindow('File Saved :  "' +
                           str(savefile.fileName) + '"  Successfully')
            self.testprogressBar.setValue(0)
        else:
            return False

    ## Swap function for re-ordering the commands ##
    def swap(self, shift_index, y_axis):
        if shift_index >= 0:
            self.objs[shift_index+1].layoutWidget.move(0, y_axis)
            self.objs[shift_index].layoutWidget.move(0, y_axis+30)
            obj = self.objs.pop(shift_index)
            self.objs.insert(shift_index+1, obj)
            self.objs[shift_index].index = shift_index
            self.objs[shift_index+1].index = shift_index+1

    ## Resize Window Event Handle ##
    def resizeEvent(self, event):
        self.width = self.scrollArea.size().width()
        for x in range(len(self.objs)):
            self.objs[x].layoutWidget.resize(int(self.width-20), 29)
        QtWidgets.QMainWindow.resizeEvent(self, event)
        QtWidgets.QScrollArea.resizeEvent(self.scrollArea, event)

    ## Insert Dialog box at given index ##
    def insertDialog(self, index):
        self.dialog = InsertDialog()
        self.dialog.btn_Devicecommand.clicked.connect(
            lambda: self.addDev(index))
        self.dialog.btn_Sleep.clicked.connect(lambda: self.addSleep(index))

    ## Add Loop Start/End Command ##
    def addLoopStartEnd(self):
        self.objs.append(Ui_Loop())
        index = len(self.objs) - 1
        if self.btn_LoopStartEnd.isChecked():
            self.btn_LoopStartEnd.setText('Loop End')
            self.objs[index].setupUi(self, 'start')
        else:
            self.btn_LoopStartEnd.setText('Loop Start/End')
            self.objs[index].setupUi(self, 'end')
        self.objs[index].index = index
        self.update()
        self.objs[index].layoutWidget.show()
        self.scrollAreaWidgetContents.setMinimumSize(
            QtCore.QSize(self.axis_y, self.axis_y))

    ## Add Device Command ##
    def addDev(self, index_insert):
        index = -1
        if index_insert != -1:
            index = index_insert + 1
            self.objs.insert(index, Ui_Device())
        else:
            self.objs.append(Ui_Device())
            index = len(self.objs) - 1
        self.objs[index].setupUi(self)
        self.objs[index].index = index
        self.update()
        self.objs[index].layoutWidget.show()
        if index_insert != -1:
            self.adjustGeometry()
        if self.dialog:
            self.dialog.close()
            self.dialog = None
        self.scrollAreaWidgetContents.setMinimumSize(
            QtCore.QSize(self.axis_y, self.axis_y))

    ## Add Sleep Command ##
    def addSleep(self, index_insert):
        index = -1
        if index_insert != -1:
            index = index_insert + 1
            self.objs.insert(index, Ui_Loop())
        else:
            self.objs.append(Ui_Loop())
            index = len(self.objs) - 1
        self.objs[index].setupUi(self, 'sleep')
        self.objs[index].index = index
        self.update()
        self.objs[index].layoutWidget.show()
        if index_insert != -1:
            self.adjustGeometry()
        if self.dialog:
            self.dialog.close()
            self.dialog = None
        self.scrollAreaWidgetContents.setMinimumSize(
            QtCore.QSize(self.axis_y, self.axis_y))

    ## Adjust Geometry of Automation Window ##
    def adjustGeometry(self):
        axis_y = 0
        for x in range(len(self.objs)):
            try:
                if self.objs[x]:
                    self.objs[x].index = x
                    self.objs[x].layoutWidget.move(0, axis_y)
                    axis_y += 30
            except Exception as e:
                print(f'line {x} error {e}')
        self.scrollAreaWidgetContents.setMinimumSize(
            QtCore.QSize(self.axis_y, self.axis_y))

    ## Find Loop Start/End ##
    def findLoopStartEnd(self, find_obj, index):
        if find_obj == 'end':
            for x in range(index, len(self.objs)):
                try:
                    if self.objs[x]:
                        if self.objs[x].objectName == 'loopEnd':
                            return x
                except Exception as e:
                    print(f'loopEnd line {x} error {e}')
        elif find_obj == 'start':
            for x in range(index, -1, -1):
                try:
                    if self.objs[x]:
                        if self.objs[x].objectName == 'loopStart':
                            return x
                except Exception as e:
                    print(f'loopStart line {x} error {e}')
        return -1

    ## Create Etree XML object and Save ##
    def save(self, filename):
        ## In case of No objects are added ##
        if len(self.objs) == 0:
            print('No Data')
            return
        root = Etree.Element('AutomationScript')
        current = root
        m1 = None
        for x in range(len(self.objs)):
            try:
                if self.objs[x]:
                    if self.objs[x].objectName == 'loopStart':
                        m1 = Etree.Element("loop")
                        count = self.objs[x].spinbox_count.value()
                        interval = self.objs[x].spinbox_interval.value()
                        if count:
                            m1.set("count", str(count))
                        else:
                            m1.set("count", '0')
                        if interval:
                            m1.set("interval", str(interval))
                        else:
                            m1.set("interval", '0')
                        current = m1
                    elif self.objs[x].objectName == 'loopEnd':
                        root.append(current)
                        current = root
                    elif self.objs[x].objectName == 'sleep':
                        s = Etree.Element("sleep")
                        interval = self.objs[x].spinbox_interval.value()
                        if interval:
                            s.set("interval", str(interval))
                        else:
                            s.set("interval", '0')
                        current.append(s)
                    elif self.objs[x].objectName == 'cmd':
                        c = Etree.Element("cmd")
                        c.set(
                            "devType", self.objs[x].comboBox_devicetype.currentText())
                        c.set(
                            "cmdName", self.objs[x].comboBox_cmd.currentText())
                        if self.objs[x].comboBox_value.isVisible():
                            v = self.objs[x].comboBox_value.currentText()
                        elif self.objs[x].spinBox_value.isVisible():
                            v = str(self.objs[x].spinBox_value.value())
                        else:
                            print("CMD value error")
                        c.set("val", v)
                        current.append(c)
            except Exception as e:
                print(f'save error {e}')
        if current == m1:
            self.btn_LoopStartEnd.setChecked(False)
            self.addLoopStartEnd()
            root.append(current)
        tree = Etree.ElementTree(root)
        Etree.indent(tree, ' ')
        # Checking if Old and New file are same
        if os.path.isfile(filename):
            oldtree = Etree.parse(filename)
            if Etree.tostring(oldtree.getroot(), encoding="utf-8") == Etree.tostring(tree.getroot(), encoding="utf-8"):
                print('No change in file')
                self.currentOpenFile = filename
                return
        with open(filename, "wb",) as files:
            tree.write(files, xml_declaration=True)
            print('Saved File Successfully')
        self.currentOpenFile = filename

    ## Load script into Automation UI ##
    def load(self, filename):
        self.old_highlight = -1
        self.clear(0, len(self.objs)-1)
        print(filename)
        tree = Etree.parse(filename)
        root = tree.getroot()
        unavaildevice = []
        for child in root:
            if child.tag == 'loop':
                self.btn_LoopStartEnd.setChecked(True)
                self.addLoopStartEnd()
                index = len(self.objs) - 1
                self.objs[index].spinbox_count.setValue(
                    int(child.attrib['count']))
                self.objs[index].spinbox_interval.setValue(
                    int(child.attrib['interval']))
                for cmd in child:
                    if cmd.tag == 'sleep':
                        self.addSleep(-1)
                        index = len(self.objs) - 1
                        self.objs[index].spinbox_interval.setValue(
                            int(cmd.attrib['interval']))
                    else:
                        self.addDev(-1)
                        index = len(self.objs) - 1
                        dt = cmd.attrib['devType']
                        if self.objs[index].comboBox_devicetype.findText(dt) > -1:
                            self.objs[index].comboBox_devicetype.setCurrentText(dt)
                            self.objs[index].comboBox_cmd.setCurrentText(
                                cmd.attrib['cmdName'])
                            if self.objs[index].spinBox_value.isVisible():
                                self.objs[index].spinBox_value.setValue(int(
                                    cmd.attrib['val']))
                            else:
                                self.objs[index].comboBox_value.setCurrentText(
                                    cmd.attrib['val'])
                        else:
                            if dt not in unavaildevice:
                                unavaildevice.append(dt)
                                print('---------', unavaildevice)
                                self.errorbox(dt + " is not onboarded!")

                self.btn_LoopStartEnd.setChecked(False)
                self.addLoopStartEnd()
            elif child.tag == 'sleep':
                self.addSleep(-1)
                index = len(self.objs) - 1
                self.objs[index].spinbox_interval.setValue(
                    int(child.attrib['interval']))
            else:
                self.addDev(-1)
                index = len(self.objs) - 1
                if self.objs[index].comboBox_devicetype.findText(child.attrib['devType']) > -1:
                    self.objs[index].comboBox_devicetype.setCurrentText(
                        child.attrib['devType'])
                    self.objs[index].comboBox_cmd.setCurrentText(
                        child.attrib['cmdName'])
                    self.objs[index].comboBox_value.setCurrentText(
                        child.attrib['val'])
                else:
                    if child.attrib['devType'] not in unavaildevice:
                        unavaildevice.append(child.attrib['devType'])
                        print('---------', unavaildevice)
                        self.errorbox(
                            child.attrib['devType']+" is not onboarded!")

        self.currentOpenFile = filename

    ## Displays the normal/abnormal status of cmd ##
    def cmd_contition(self, x, normal):
        if normal:
            self.objs[x].layoutWidget.setStyleSheet('background-color: white;')
        else:
            self.objs[x].layoutWidget.setStyleSheet('background-color: red;')

    ## Validate All Fields ##
    def validatefield(self):
        valid = True
        if len(self.objs) == 0:
            self.errorbox('No Data')
            valid = False
            return valid
        for x in range(len(self.objs)):
            try:
                if self.objs[x]:
                    if self.objs[x].objectName == 'loopStart':
                        if self.objs[x].spinbox_count.value() <= 0:
                            self.cmd_contition(x, False)
                            valid = False
                        else:
                            self.cmd_contition(x, True)
                    elif self.objs[x].objectName == 'sleep':
                        if self.objs[x].spinbox_interval.value() <= 0:
                            self.cmd_contition(x, False)
                            valid = False
                        else:
                            self.cmd_contition(x, True)
                    elif self.objs[x].objectName == 'cmd':
                        devtype = self.objs[x].comboBox_devicetype.currentText()
                        cmdtype = self.objs[x].comboBox_cmd.currentText()
                        if devtype == 'Device Type':
                            self.cmd_contition(x, False)
                            valid = False
                        elif (LIGHTSENSOR_DEVICE_TYPE in devtype) and ("Level Control lux" in cmdtype):
                            try:
                                input = self.objs[x].spinBox_value.value()
                            except ValueError:
                                self.cmd_contition(x, False)
                                valid = False
                            else:
                                if input < LIGHTSENSOR_MIN_VAL or input > LIGHTSENSOR_MAX_VAL:
                                    self.cmd_contition(x, False)
                                    self.errorbox(
                                        f'{LIGHTSENSOR_MIN_VAL} &lt; Light Sensor &gt; {LIGHTSENSOR_MAX_VAL}')
                                    valid = False
                                else:
                                    measured_value = Utils.findMeasuredValue(input)
                                    convert_illum = Utils.toIlluminance(measured_value)
                                    self.objs[x].spinBox_value.setValue(convert_illum)
                                    self.cmd_contition(x, True)
                        else:
                            self.cmd_contition(x, True)
            except Exception as e:
                print(f'validatefield error {e}')
        if valid == False:
            self.errorbox('Please fill required fields')
        return valid

    ## Common ErrorBox ##
    @staticmethod
    def errorbox(message):
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage(message)
        error_dialog.setWindowModality(QtCore.Qt.WindowModal)
        error_dialog.setWindowTitle('Error')
        error_dialog.exec()

    ## Clear UX objects ##
    def clear(self, start, stop):
        # Stop clearing while script is running
        if self.btn_Run.isChecked():
            self.errorbox('Please wait, Script is Running')
            return
        diff = stop - start + 1
        while (diff):
            try:
                if self.objs[start]:
                    self.objs[start].layoutWidget.deleteLater()
                    del self.objs[start]
                    diff -= 1
                    self.axis_y -= 30
            except Exception as e:
                print(f'clear error {e}')
        self.adjustGeometry()
        self.scrollAreaWidgetContents.setMinimumSize(
            QtCore.QSize(self.axis_y, self.axis_y))
        if len(self.objs) == 0:
            self.currentOpenFile = None
            self.btn_LoopStartEnd.setChecked(False)
            self.btn_LoopStartEnd.setText('Loop Start/End')
            self.testprogressBar.setValue(0)
            self.logwindow('Clean all')

    def silentToggleBtnRun(self):
        self.btn_Run.setCheckable(False)
        self.btn_Run.toggle()
        self.btn_Run.setCheckable(True)

    ## Run Test Script ##
    @QtCore.pyqtSlot(bool)
    def run(self, state):
        if state:
            if not self.validatefield():
                print('Validation Failed')
                self.silentToggleBtnRun()
                return
            else:
                if self.currentOpenFile == None:
                    if self.savefile(1) == False:
                        self.silentToggleBtnRun()
                        self.errorbox('Please Save a file before Run')
                        return
                else:
                    self.save(self.currentOpenFile)
            self.curcmd = 0
            self.send_device_number(self.currentOpenFile)
            self.testprogressBar.setValue(0)
            self.logtrack = LogTrackScriptCntl()
            self.autotestThread = ProcessCmd(self, self.currentOpenFile)
            self.autotestThread.update_highlight.connect(self.highlight)
            self.autotestThread.complete_autotest.connect(
                self.complete_autotest)
            self.autotestThread.totalCmd(self)
            self.testprogressBar.setMaximum(self.totalcmd)
            self.logwindow('Automation Test Started')
            self.btn_Run.setStyleSheet(
                'background-color: red;font-weight: bold;font: 16pt;font-weight: bold;')
            self.btn_Run.setText('Stop')
            self.logtrack.launch_log_track_script()
            while (not self.use_test_window and not self.logtrack.checksuccessfile()):
                QTest.qWait(100)
            self.autotestThread.start()
            self.autotestComplete = False
        else:
            self.btn_Run.setCheckable(False)
            if self.autotestThread and not self.autotestThread.exec_stop:
                self.autotestThread.update_highlight.disconnect(self.highlight)
                self.autotestThread.complete_autotest.disconnect(
                    self.complete_autotest)
                self.autotestThread.stop()
                self.autotestThread = 0

            if self.autotestComplete:
                self.logwindow('Automation Test completed')
            else:
                self.logwindow('Automation Test stoped')
            self.logtrack.terminate_log_track_script()
            self.logwindow("Successful commands: " +
                           str(self.logtrack.successcount(self.currentOpenFile)))
            if self.logtrack.filename != None:
                self.logwindow("Test report stored at " +
                               self.logtrack.filename)
            self.logtrack = 0
            self.btn_Run.setText('Run')
            self.btn_Run.setStyleSheet(
                'background-color: rgb(98, 160, 234);font: 16pt;font-weight:bold;')
            if self.old_highlight != -1:
                self.objs[self.old_highlight].layoutWidget.setStyleSheet('')
                self.old_highlight = -1
            self.btn_Run.setCheckable(True)
            self.send_device_number()

    ## Highlight Executing command ##
    def highlight(self, index):
        if not self.autotestThread:
            self.objs[self.old_highlight].layoutWidget.setStyleSheet('')
            self.testprogressBar.setValue(self.curcmd+1)
            self.curcmd += 1
            return
        if self.old_highlight != -1:
            self.objs[self.old_highlight].layoutWidget.setStyleSheet('')
        self.objs[index].layoutWidget.setStyleSheet(
            'background-color: blue;font-weight:bold')
        self.objs[index].layoutWidget.show()
        self.testprogressBar.setValue(self.curcmd+1)
        self.curcmd += 1
        self.old_highlight = index
        QTest.qWait(200)
        return

    ## Close event from main window ##
    def force_closeEvent(self, device):
        if (device & ForceClose.AUTOMATION) and not self.force_quit:
            print('quit automation test')
            self.force_quit = True
            if self.autotestThread:
                self.autotestThread.stop()
            if self.logtrack:
                self.logtrack.terminate_log_track_script()
            self.close()

    ## Device remove event ##
    @QtCore.pyqtSlot(str)
    def removed_device(self, device_num):
        if self.force_quit:
            return
        print('removed_device : ' + device_num)
        id = None
        error = False
        for obj in self.objs:
            if obj.objectName == 'cmd':
                if id is None:
                    id = obj.comboBox_devicetype.findText(
                        device_num, Qt.MatchContains)
                if obj.comboBox_devicetype.currentIndex() == id:
                    if self.autotestThread and not self.autotestThread.exec_stop:
                        self.autotestThread.complete_autotest.emit()
                        while (self.autotestThread and not self.autotestThread.exec_stop):
                            QTest.qWait(100)
                    if not error:
                        self.logwindow(
                            obj.comboBox_devicetype.currentText()+' is removed')
                        self.errorbox(
                            obj.comboBox_devicetype.currentText()+' is removed')
                        error = True
                    obj.comboBox_devicetype.setCurrentIndex(0)
                obj.comboBox_devicetype.removeItem(id)


    ## Complete Automation test ##
    @QtCore.pyqtSlot()
    def complete_autotest(self):
        print('Complete automation test')
        if self.autotestThread and not self.autotestThread.exec_stop:
            self.btn_Run.toggle()
            self.autotestComplete = True

    ## Send device number for Automation##
    def send_device_number(self, xmlFile=None):
        used_device_dict = dict()
        used_device_list = self.devMgrObj.get_used_devices()
        for device in used_device_list:
            if device.get_commissioning_state():
                used_device_dict[device.get_device_num()] = False

        if xmlFile is not None:
            cmdTree = ET.parse(xmlFile)
            rootCmd = cmdTree.getroot()
            for element in rootCmd:
                if (element.tag == 'cmd'):
                    self.check_device_number(element, used_device_dict)
                elif (element.tag == 'loop'):
                    for child in element.findall('cmd'):
                        self.check_device_number(child, used_device_dict)

        self.send_used_list.emit(used_device_dict)

    ## Check device number ##
    def check_device_number(self, element, used_device_dict):
        device_number = element.get('devType').split("-")[1]
        used_device_dict[device_number] = True

