import os.path
import time
from PyQt5.QtCore import *
from datetime import datetime


class PipeThread(QThread):
    msg_changed = pyqtSignal(str)
    state_updated = pyqtSignal(bool)
    setup_code = pyqtSignal(str)
    received_qrcode = pyqtSignal(str)

    def __init__(self, deviceNum):
        super().__init__()
        self.deviceNum = deviceNum

    def run(self):
        FIFO_FILENAME = '/tmp/chip_pipe_device' + self.deviceNum
        if not os.path.exists(FIFO_FILENAME):
            os.mkfifo(FIFO_FILENAME)
        fp_fifo = open(FIFO_FILENAME, "r")

        while True:
            data = fp_fifo.readline().rstrip('\n')
            if data:
                now = datetime.now()
                print("[%s][%s] %s" % (str(now), self.deviceNum, data))
                self.msg_changed.emit(data)  # send to main thread

    def stop(self):
        self.quit()
        time.sleep(1)
