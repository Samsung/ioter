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
# File : filedialog.py
# Description:
# Handle opening and saving of Automation script.

from automation.ProcessCmd import ProcessCmd

from PyQt5.QtWidgets import QWidget, QFileDialog

## Setup File Open/Save UX ##
class FileDialog(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Automation Script'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.fileName = None
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

    ## Open XML Files ##
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(
            self, "Open XML File", ProcessCmd.mScriptFilePath, "XML Files (*.xml)", options=options)
        if self.fileName:
            print(self.fileName)

    ## Open All format Files ##
    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(
            self, "Open Files", "", "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)

    ## Save XML Files ##
    def saveFileDialog(self):
        fd = QFileDialog(self, "Save XML File", ProcessCmd.mScriptFilePath, "XML Files (*.xml)")
        fd.setDefaultSuffix("xml")
        fd.setOptions(QFileDialog.DontUseNativeDialog)
        fd.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        fd.exec()
        if fd.selectedFiles()[0] == fd.directory().absolutePath():
            print("File is not selected")
            self.fileName = ""
        else:
            print(self.fileName)
            self.fileName = fd.selectedFiles()[0]

