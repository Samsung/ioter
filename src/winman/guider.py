from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget

"""
    It shows rectangles indicate empty space
"""


class Guider(QWidget):
    def __init__(self, rectangles):
        super().__init__()
        self.rectangles = []
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        for r in rectangles:
            tmp = QRect(r.x, r.y, r.w, r.h)
            self.rectangles.append(tmp)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 0, 0, 200))
        for r in self.rectangles:
            painter.drawRect(r)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
