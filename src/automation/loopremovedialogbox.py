########### Loop Removal Box #############
from common.utils import Utils

from PyQt5 import QtCore, QtWidgets, uic


class LoopRemoveDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(Utils.get_view_path("loopremovedialog.ui"), self)
        self.setWindowTitle('Loop Removal')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setStyleSheet('font-weight:bold')
        self.show()
