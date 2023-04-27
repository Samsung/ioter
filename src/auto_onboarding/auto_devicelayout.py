from common.utils import Utils
from common.device_command import *

from PyQt5 import QtCore, QtWidgets
import os


class auto_device(object):
    index = 0

    def setupUi(self, parent, comport, vendor):
        self.parent = parent
        self.comport = comport
        self.objectName = "device"
        self.layoutWidget = QtWidgets.QWidget(parent.scrollAreaWidgetContents)
        self.layoutWidget.setGeometry(QtCore.QRect(
            0, parent.axis_y, parent.width-20, 29))
        parent.axis_y += 30
        self.layoutWidget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.chkbox = QtWidgets.QCheckBox(self.layoutWidget)
        self.chkbox.setObjectName("chkbox")
        self.chkbox.setMinimumWidth(15)
        self.chkbox.setMaximumWidth(30)
        self.horizontalLayout.addWidget(self.chkbox)
        self.usb_device_label = QtWidgets.QLabel(self.layoutWidget)
        self.usb_device_label.setObjectName("usbLabel")
        self.usb_device_label.setText(str(comport)+"/"+str(vendor))
        self.usb_device_label.setMinimumWidth(175)
        self.usb_device_label.setMaximumWidth(250)
        self.horizontalLayout.addWidget(self.usb_device_label)
        self.combo_device_type = QtWidgets.QComboBox(self.layoutWidget)
        self.combo_device_type.setObjectName("devicetype")
        self.horizontalLayout.addWidget(self.combo_device_type)
        self.combo_thread_type = QtWidgets.QComboBox(self.layoutWidget)
        self.combo_thread_type.setObjectName("threadtype")
        self.combo_thread_type.setMinimumWidth(120)
        self.horizontalLayout.addWidget(self.combo_thread_type)
        self.combo_debug_level = QtWidgets.QComboBox(self.layoutWidget)
        self.combo_debug_level.setObjectName("debuglevel")
        self.combo_debug_level.addItems(["1", "2", "3", "4", "5"])
        self.combo_debug_level.setMinimumWidth(70)
        self.combo_debug_level.setMaximumWidth(70)
        self.horizontalLayout.addWidget(self.combo_debug_level)
        self.discriminator = QtWidgets.QSpinBox(self.layoutWidget)
        self.discriminator.setObjectName("discriminator")
        self.discriminator.setRange(1000, 9999)
        self.discriminator.setMinimumWidth(80)
        self.discriminator.setMaximumWidth(80)
        self.horizontalLayout.addWidget(self.discriminator)
        self.status = QtWidgets.QLabel("ready")
        self.status.setObjectName("status")
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        self.status.setMinimumWidth(100)
        self.horizontalLayout.addWidget(self.status)

        self.insert_comboBox()
        QtCore.QMetaObject.connectSlotsByName(parent)

    def insert_comboBox(self):
        self.combo_thread_type.addItems(self.get_thread_type_list())
        self.combo_device_type.addItems(CommandUtil.device_type_id.keys())

    def get_thread_type_list(self):
        version = []
        list = os.listdir(Utils.get_thread_lib_path())
        filtered_list = [thread for thread in list if thread.startswith(
            Utils.get_thread_lib_prefix())]
        for file in filtered_list:
            version.append(file[len(Utils.get_thread_lib_prefix()):])
        return version

    def set_status(self):
        self.status.setText()
