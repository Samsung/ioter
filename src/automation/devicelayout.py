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
# File : devicelayout.py
# Description:
# Setup Device command Layout.

from common.device_command import *

from PyQt5 import QtCore, QtGui, QtWidgets
import xml.etree.ElementTree as Etree


class Ui_Device(object):
    index = 0

    ## Setup Device command Layout ##
    def setupUi(self, parent):
        self.range = dict()
        self.objectName = 'cmd'
        self.layoutWidget = QtWidgets.QWidget(parent.scrollAreaWidgetContents)
        self.layoutWidget.setGeometry(QtCore.QRect(
            0, parent.axis_y, int(parent.scrollArea.size().width()-20), 29))
        parent.axis_y += 30
        self.layoutWidget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox_devicetype = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_devicetype.setStyleSheet(
            "background-color: rgb(255, 163, 72);")
        self.comboBox_devicetype.setObjectName("devicetype")
        self.comboBox_devicetype.addItem("Device Type")
        self.comboBox_devicetype.currentIndexChanged.connect(
            lambda: self.changecomboBox_devicetype(parent))
        self.horizontalLayout.addWidget(self.comboBox_devicetype)
        self.comboBox_cmd = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_cmd.setObjectName("cmd")
        self.comboBox_cmd.addItem("")
        self.comboBox_cmd.currentIndexChanged.connect(self.changecomboBox_cmd)
        self.horizontalLayout.addWidget(self.comboBox_cmd)
        self.comboBox_value = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_value.setObjectName("value")
        self.comboBox_value.currentIndexChanged.connect(
            self.changecomboBox_value)
        self.horizontalLayout.addWidget(self.comboBox_value)
        self.btn_remove = QtWidgets.QToolButton(self.layoutWidget)
        self.btn_remove.setObjectName("remove")
        self.btn_remove.clicked.connect(lambda: self.deleteSelf(parent))
        self.horizontalLayout.addWidget(self.btn_remove)
        self.btn_insert = QtWidgets.QToolButton(self.layoutWidget)
        self.btn_insert.setObjectName("insert")
        self.btn_insert.clicked.connect(lambda: self.addnew(parent))
        self.horizontalLayout.addWidget(self.btn_insert)
        self.btn_up = QtWidgets.QToolButton(self.layoutWidget)
        self.btn_up.setObjectName("UP")
        self.btn_up.clicked.connect(lambda: self.move_up_down("UP", parent))
        self.horizontalLayout.addWidget(self.btn_up)
        self.btn_down = QtWidgets.QToolButton(self.layoutWidget)
        self.btn_down.setObjectName("Down")
        self.btn_down.clicked.connect(
            lambda: self.move_up_down("DOWN", parent))
        self.horizontalLayout.addWidget(self.btn_down)
        self.retranslateUi(parent)
        self.datainsert(parent)
        QtCore.QMetaObject.connectSlotsByName(parent)

    ## Retranslate UI ##
    def retranslateUi(self, parent):
        _translate = QtCore.QCoreApplication.translate
        self.btn_remove.setText(_translate("parent", "-"))
        self.btn_insert.setText(_translate("parent", "+"))
        self.btn_up.setText(_translate("parent", "↑"))
        self.btn_down.setText(_translate("parent", "↓"))

    ## Insert Data ##
    def datainsert(self, parent):
        for device in parent.devMgrObj.get_used_devices():
            if device.get_commissioning_state():
                num = device.get_device_num()
                self.comboBox_devicetype.addItem(
                    CommandUtil. get_device_type_by_device_id(device. get_device_id())+'-'+num)

    ## Show Device Type And respective Commands ##
    def changecomboBox_devicetype(self, parent):
        self.comboBox_cmd.clear()
        devicetype = self.comboBox_devicetype.currentText()
        if devicetype == 'Device Type':
            return
        devicenum = devicetype.split('-')[1]
        cmdlist = parent.commandList[devicenum]
        for cmd in cmdlist:
            if 'val' in cmd.keys():
                self.comboBox_cmd.addItem(cmd['Name'], cmd['val'])
            elif 'range' in cmd.keys():
                data = []
                numbers = range(int(cmd['range'][0]), int(cmd['range'][1])+1)
                if len(numbers) <= 10001 :
                    for x in numbers:
                        data.append(str(x))
                else:
                    data.append(f"Range {cmd['range'][0]} ~ {cmd['range'][1]}")
                self.comboBox_cmd.addItem(cmd['Name'], data)
        self.comboBox_cmd.show()

    ## Change Combo Box Command ##
    def changecomboBox_cmd(self, index):
        self.comboBox_value.clear()
        if index == -1:
            return
        cmds = self.comboBox_cmd.itemData(index)
        index = self.comboBox_cmd.currentIndex()
        self.range[index] = cmds[0]
        self.comboBox_value.addItems(cmds)
        self.comboBox_value.show()

    ## Change Combo Box Value ##
    def changecomboBox_value(self, index):
        index = self.comboBox_cmd.currentIndex()
        count = self.comboBox_value.count()
        self.comboBox_value.setToolTip("")
        msg = self.range.get(index, None)
        if count <= 1 and msg:
            self.comboBox_value.setToolTip(msg)
            self.comboBox_value.setEditable(True)
            try:
                int(self.comboBox_value.currentText())
            except:
                self.comboBox_value.clear()
        elif count > 2:
            self.comboBox_value.setEditable(True)
            self.comboBox_value.setEditable(False)
        else:
            self.comboBox_value.setEditable(False)

    ## Removing Objects ##
    def deleteSelf(self, parent):
        print('removing obj...')
        self.layoutWidget.setParent(None)
        self.layoutWidget.deleteLater
        parent.axis_y -= 30
        parent.objs.remove(self)
        parent.adjustGeometry()

    ## Calling Insert Dialog Function ##
    def addnew(self, parent):
        parent.insertDialog(self.index)

    ## Move commands Up and Down ##
    def move_up_down(self, move, parent):
        y_axis = self.layoutWidget.pos().y()
        if move == "UP":
            if self.index > 0:
                parent.swap(self.index-1, y_axis-30)
        elif move == "DOWN":
            if self.index+1 < len(parent.objs):
                parent.swap(self.index, y_axis)
