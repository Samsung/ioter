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
# File : ProcessCmd.py
# Description:
# executing and Processing Automation Script Commands.


# Automation of Matter Device Emulator
from common.manage_device import *
from common.device_command import *

import sys
import os
import xml.etree.ElementTree as ET
from PyQt5.QtCore import *
from PyQt5.QtTest import *

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

# from enum import Enum

# ============================ ExecuteCmd class   ========================================


class ExecuteCmd:

    # Class Variable
    CMD_0 = 0
    CMD_1 = 1
    CMD_2 = 2
    CMD_3 = 3

    ## The init method or constructor ##
    def __init__(self, commandList, aDevType, aCmd, aCmdVal):
        self.devType = aDevType[0:aDevType.find('-')]
        self.cmd = aCmd
        self.cmdVal = aCmdVal
        self.devNum = aDevType[len(self.devType)+len('-'):]

    ## Execute commands ##
    def execCmd(self):
        print('execCmd' + ' + ' + self.devType)
        for cmd in self.command:
            if (self.cmd == cmd['Name']):
                execmd = cmd['Set_val']
                execmd(self.cmdVal)
                execmd = cmd['Get_val']
                value = execmd()
                print(f"get_val {value}")
                return
        print(f'ERROR: Unknown Command {self.cmd}-{self.cmdVal} devNum {self.devNum}')

    def __str__(self):
        return "devType:{1}, cmd:{2}, cmdVal:{3}, devNum:{1}".format(self.devType, self.cmd, self.cmdVal, self.devNum)


# ============================ ProcessCmd class   ========================================
class ProcessCmd(QThread):
    update_highlight = pyqtSignal(int)
    complete_autotest = pyqtSignal()
    # Class Variable
    mDevConfFilepath = 'src/automation/conf/'
    mScriptFilePath = 'src/automation/output/'

    ## The init method or constructor
    def __init__(self, aUiObj, aFilePath):
        super().__init__()
        print('ProcessCmd init')
        self.parent = parent
        self.scriptFilePath = aFilePath

        self.exec_stop = False
        self.count = 0

    ##  Give Total Command ##
    def totalCmd(self, parent):
        cmdTree = ET.parse(self.scriptFilePath)
        parent.totalcmd = 0
        rootCmd = cmdTree.getroot()
        for element in rootCmd:
            if (element.tag == 'sleep'):
                parent.totalcmd += 1
            elif (element.tag == 'loop'):
                maxCnt = int(element.get('count'))
                totalchild = 0
                totalchild += len(element.findall('cmd'))
                totalchild += len(element.findall('sleep'))
                parent.totalcmd = parent.totalcmd + maxCnt*totalchild + 1
            else:
                parent.totalcmd += 1
        print('Total Commands ->', parent.totalcmd)

    ## Run Command ##
    def run(self):
        print('Run Cmd')

        # read/extract command list from XML
        cmdTree = ET.parse(self.scriptFilePath)

        rootCmd = cmdTree.getroot()
        uiIdx = 0
        for element in rootCmd:
            if self.exec_stop:
                break
            print(element.tag, element.attrib)
            print('++++++++++++++++')
            if (element.tag == 'sleep'):
                sleepInterval = int(element.get('interval'))
                print('Sleep->', sleepInterval)
                self.send_highlight(uiIdx)
                uiIdx += 1
                self.setSleep(sleepInterval)

            elif (element.tag == 'loop'):
                curCnt = 1
                maxCnt = int(element.get('count'))
                loopInterval = int(element.get('interval'))
                self.send_highlight(uiIdx)
                uiIdx += 1
                totalchild = 0
                totalchild += len(element.findall('cmd'))
                totalchild += len(element.findall('sleep'))
                while curCnt <= maxCnt:
                    if self.exec_stop:
                        return
                    for child, x in zip(element, range(uiIdx, uiIdx+totalchild)):
                        if self.exec_stop:
                            return
                        self.send_highlight(x)
                        if (child.tag == 'sleep'):
                            sleepInterval = int(child.get('interval'))
                            print('Sleep->', sleepInterval)
                            self.setSleep(sleepInterval)
                        else:
                            print(child.tag, child.attrib)
                            ExecuteCmd(self.parent.commandList, child.get('devType'), child.get(
                                'cmdName'), child.get('val')).execCmd()
                            self.setSleep(1)
                    print('Current Loop Count->', curCnt)
                    curCnt += 1

                    self.setSleep(loopInterval)
                uiIdx += totalchild
                self.send_highlight(uiIdx)
                uiIdx += 1
            else:
                ExecuteCmd(self.parent.commandList, element.get('devType'), element.get(
                    'cmdName'), element.get('val')).execCmd()
                self.send_highlight(uiIdx)
                uiIdx += 1
                self.setSleep(1)
        self.complete_autotest.emit()

    ## Set Sleep ##
    def setSleep(self, delaytime):
        count = 0
        while not self.exec_stop:
            if delaytime <= count:
                break
            QTest.qWait(1000)
            count += 1

    ## Send Highlighting Index ##
    def send_highlight(self, pos):
        if not self.exec_stop:
            self.update_highlight.emit(pos)
            QTest.qWait(200)

    ## Stop Execution of  Automation Script ##
    def stop(self):
        self.exec_stop = True
        self.quit()
        QTest.qWait(1000)
