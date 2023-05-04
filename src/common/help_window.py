from common.utils import Utils

from PyQt5 import uic
from PyQt5.QtWidgets import *

from typing import Final

GITHUB_LINK: Final = "<a href=\"https://github.com/Samsung/ioter\">https://github.com/Samsung/ioter</a>"

class HelpWindow(QDialog):
    def __init__(self, parent, title):
        super(HelpWindow, self).__init__()
        uic.loadUi(Utils.get_view_path('main_help.ui'), self)
        self.setWindowTitle("About" + " " + title)
        self.titleLabel.setText("Version" + " " + Utils.get_version())
        self.githubLabel.setText(GITHUB_LINK)
        self.githubLabel.setOpenExternalLinks(True)
