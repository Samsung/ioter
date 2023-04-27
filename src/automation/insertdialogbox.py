###### Insert Command Box ############
from common.utils import Utils

from PyQt5 import QtWidgets, uic


class InsertDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(Utils.get_view_path("insertdialog.ui"), self)
        self.setWindowTitle('Insert')
        self.show()
