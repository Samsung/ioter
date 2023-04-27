################ Setup File Open/Save UX ##########
from automation.ProcessCmd import ProcessCmd

from PyQt5.QtWidgets import QWidget, QFileDialog


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

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(
            self, "Open XML File", ProcessCmd.mScriptFilePath, "XML Files (*.xml)", options=options)
        if self.fileName:
            print(self.fileName)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(
            self, "Open Files", "", "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getSaveFileName(
            self, "Save XML File", ProcessCmd.mScriptFilePath, "XML Files (*.xml)", options=options)
        if self.fileName:
            print(self.fileName)
