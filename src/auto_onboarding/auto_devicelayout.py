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
# File : auto_devicelayout.py
# Description:
# Handles UI Setup of automation

from common.utils import Utils
from common.device_command import *

from PyQt5 import QtCore, QtWidgets
import os

## Automation of devices ##
class auto_device(object):
    index = 0

    ## UI setup ##
    def setupUi(self, parent, comport, vendor):
        self.parent = parent
        self.comport = comport
        self.objectName = "device"
        self.device_name = ""
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

    ## Insert Combo Box ##
    def insert_comboBox(self):
        self.combo_thread_type.addItems(self.get_thread_type_list())
        self.combo_device_type.addItems(CommandUtil.device_type_id.keys())

    ## Get thread type ##
    def get_thread_type_list(self):
        version = []
        list = os.listdir(Utils.get_thread_lib_path())
        filtered_list = [thread for thread in list if thread.startswith(
            Utils.get_thread_lib_prefix())]
        for file in filtered_list:
            version.append(file[len(Utils.get_thread_lib_prefix()):])
        return version

    ## Set status ##
    def set_status(self):
        self.status.setText()
