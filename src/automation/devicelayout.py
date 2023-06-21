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

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Ui_Device(object):
    index = 0

    ## Setup Device command Layout ##
    def setupUi(self, parent):
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
        self.commandList = parent.commandList
        self.comboBox_devicetype.currentIndexChanged.connect(
            self.changecomboBox_devicetype)
        self.horizontalLayout.addWidget(self.comboBox_devicetype)

        self.comboBox_cmd = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_cmd.setObjectName("cmd")
        self.comboBox_cmd.addItem("")
        self.comboBox_cmd.currentIndexChanged.connect(self.changecomboBox_cmd)
        self.horizontalLayout.addWidget(self.comboBox_cmd)

        self.spinBox_value = QtWidgets.QSpinBox(self.layoutWidget)
        self.spinBox_value.setObjectName("spin_value")
        self.spinBox_value.hide()
        self.horizontalLayout.addWidget(self.spinBox_value)

        self.comboBox_value = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_value.setObjectName("value")
        self.comboBox_value.hide()
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
                    CommandUtil.get_device_type_by_device_id(device.get_device_id())+'-'+num)

    ## Get ['Device name', 'Device number']
    def getDeviceType(self):
        devicetype = self.comboBox_devicetype.currentText()
        if devicetype == 'Device Type':
            return ["", -1]
        return devicetype.split('-')

    ## Get command list for current device
    def getCmdList(self):
        devicenum = self.getDeviceType()[1]
        if devicenum == -1:
            return []
        return self.commandList[devicenum]

    ## Show Device Type And respective Commands ##
    def changecomboBox_devicetype(self):
        self.comboBox_cmd.clear()
        for cmd in self.getCmdList():
            if 'val' in cmd.keys():
                self.comboBox_cmd.addItem(cmd['Name'], cmd['val'])
            elif 'range' in cmd.keys():
                minmax = (int(cmd['range'][0]), int(cmd['range'][1]))
                self.comboBox_cmd.addItem(cmd['Name'], minmax)

    ## Change Combo Box Command ##
    def changecomboBox_cmd(self, index):
        if index == -1:
            return
        data = self.comboBox_cmd.itemData(index)
        if type(data) is tuple:
            self.changeSpinBox_value(self.comboBox_cmd.itemText(index), data[0], data[1])
        else:
            self.changecomboBox_value(data)

    ## Change Spin Box Value ##
    def changeSpinBox_value(self, item_text, min, max):
        self.spinBox_value.setRange(min, max)
        device_name = self.getDeviceType()[0]
        if device_name == LIGHTSENSOR_DEVICE_TYPE:
            self.spinBox_value.setSuffix(LIGHTSENSOR_UNIT)
        self.spinBox_value.setToolTip(f"Range {min} ~ {max}")
        self.spinBox_value.show()
        self.comboBox_value.hide()

    ## Change Combo Box Value ##
    def changecomboBox_value(self, items):
        self.comboBox_value.clear()
        self.comboBox_value.addItems(items)
        self.comboBox_value.show()
        self.spinBox_value.hide()

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
