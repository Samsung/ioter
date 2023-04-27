from common.device_command import CommandUtil

from PyQt5 import QtCore, QtGui, QtWidgets
import xml.etree.ElementTree as Etree


class Ui_Device(object):
    index = 0
########## Setup Device command Layout ##########

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

    def retranslateUi(self, parent):
        _translate = QtCore.QCoreApplication.translate
        self.btn_remove.setText(_translate("parent", "-"))
        self.btn_insert.setText(_translate("parent", "+"))
        self.btn_up.setText(_translate("parent", "↑"))
        self.btn_down.setText(_translate("parent", "↓"))

    def datainsert(self, parent):
        print(len(parent.devMgrObj.get_used_devices()))
        for device in parent.devMgrObj.get_used_devices():
            if device.get_commissioning_state():
                num = device.get_device_num()
                self.comboBox_devicetype.addItem(
                    CommandUtil. get_device_type_by_device_id(device. get_device_id())+'-'+num)

    def changecomboBox_devicetype(self, parent):
        self.comboBox_cmd.clear()
        devicetype = self.comboBox_devicetype.currentText()
        if devicetype == 'Device Type':
            return
        devicetype = devicetype.split('-')
        cmdlist = CommandUtil.get_command_list_by_device_type(devicetype[0])
        for cmd in cmdlist:
            if 'val' in cmd.keys():
                self.comboBox_cmd.addItem(cmd['Name'], cmd['val'])
            elif 'range' in cmd.keys():
                data = []
                for x in range(int(cmd['range'][0]), int(cmd['range'][1])+1):
                    data.append(str(x))
                self.comboBox_cmd.addItem(cmd['Name'], data)
        self.comboBox_cmd.show()

    def changecomboBox_cmd(self, index):
        self.comboBox_value.clear()
        if index == -1:
            return
        cmds = self.comboBox_cmd.itemData(index)
        self.comboBox_value.addItems(cmds)
        devtype = self.comboBox_devicetype.currentText()
        if 'Temperature' in devtype:
            self.comboBox_value.setEditable(True)
        else:
            self.comboBox_value.setEditable(False)
        self.comboBox_value.show()

    def changecomboBox_value(self, index):
        devtype = self.comboBox_devicetype.currentText()
        if 'Temperature' in devtype:
            try:
                int(self.comboBox_value.currentText())
            except:
                self.comboBox_value.clear()

    def deleteSelf(self, parent):
        print('removing obj...')
        self.layoutWidget.setParent(None)
        self.layoutWidget.deleteLater
        parent.axis_y -= 30
        parent.objs.remove(self)
        parent.adjustGeometry()

    def addnew(self, parent):
        parent.insertDialog(self.index)

    def move_up_down(self, move, parent):
        y_axis = self.layoutWidget.pos().y()
        if move == "UP":
            if self.index > 0:
                parent.swap(self.index-1, y_axis-30)
        elif move == "DOWN":
            if self.index+1 < len(parent.objs):
                parent.swap(self.index, y_axis)
