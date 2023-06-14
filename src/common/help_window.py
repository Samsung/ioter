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
# File : help_window.py
# Description: Show help window

from common.utils import Utils

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QTextCursor
from typing import Final

GITHUB_LINK: Final = "<a href=\"https://github.com/Samsung/ioter\">https://github.com/Samsung/ioter</a>"

## Help Window class ##
class HelpWindow(QDialog):
    def __init__(self, parent, title, version):
        super(HelpWindow, self).__init__()
        uic.loadUi(Utils.get_view_path('main_help.ui'), self)
        self.setWindowTitle("About" + " " + title)
        self.titleLabel.setText("Version" + " " + version)
        self.githubLabel.setText("Home: " + GITHUB_LINK)
        self.githubLabel.setOpenExternalLinks(True)
        with open(Utils.get_base_path() + 'LICENSE', encoding='utf8') as f:
            for line in f:
                self.licenseBrowser.append(line)
        self.licenseBrowser.moveCursor(QTextCursor.Start)
