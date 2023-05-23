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
# File : ioterPipe.py
# Description: Manage linux pipes for device commands

import os.path
import time
from PyQt5.QtCore import *
from datetime import datetime

## Main pipe class ##
class PipeThread(QThread):
    msg_changed = pyqtSignal(str)
    state_updated = pyqtSignal(bool)
    setup_code = pyqtSignal(str)
    received_qrcode = pyqtSignal(str)

    ## Initiate Pipe class thread ##
    def __init__(self, deviceNum):
        super().__init__()
        self.deviceNum = deviceNum

    ## Create Pipe with device number ##
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

    ## Stopr pipe thread ##
    def stop(self):
        self.quit()
        time.sleep(1)
