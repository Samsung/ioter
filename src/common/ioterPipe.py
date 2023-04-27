import os.path
import time
from PyQt5.QtCore import *
from datetime import datetime


class PipeThread(QThread):
    msg_changed = pyqtSignal(str)
    state_updated = pyqtSignal(bool)
    setup_code = pyqtSignal(str)
    received_qrcode = pyqtSignal(str)

    # 초기화 메서드 구현
    def __init__(self, deviceNum):
        super().__init__()
        self.deviceNum = deviceNum

    def run(self):
        # 쓰레드로 동작시킬 함수 내용 구현
        FIFO_FILENAME = '/tmp/chip_pipe_device' + self.deviceNum
        if not os.path.exists(FIFO_FILENAME):
            os.mkfifo(FIFO_FILENAME)
        if os.path.exists(FIFO_FILENAME):
            fp_fifo = open(FIFO_FILENAME, "r")

        while True:
            with open(FIFO_FILENAME, 'r') as fifo:
                data = fifo.read()
                line = data.split('\n')
                # print(line)

            for msg in line:
                if msg != '':
                    now = datetime.now()
                    print("[%s] %s" % (str(now), msg))
                    self.msg_changed.emit(msg)  # send to main thread

    def stop(self):
        self.quit()
        time.sleep(1)
