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
    CMD_1 = 0
    CMD_2 = 1
    CMD_3 = 2

    # The init method or constructor
    def __init__(self, aDevType, aCmd, aCmdVal):
        print('ExecuteCmd init')
        self.devType = aDevType[0:aDevType.find('-')]
        self.cmd = aCmd
        self.cmdVal = aCmdVal
        self.devNum = aDevType[len(self.devType)+len('-'):]

    def execCmd(self):
        print('execCmd' + ' + ' + self.devType)
        if (self.devType == LIGHTBULB_DEVICE_TYPE):
            self.execLightBulbCmd()
        elif (self.devType == DOORLOCK_DEVICE_TYPE):
            self.execDoorLockCmd()
        elif (self.devType == CONTACTSENSOR_DEVICE_TYPE):
            self.execContactSensorCmd()
        elif (self.devType == TEMPERATURE_DEVICE_TYPE):
            self.execTemperatureCmd()
        elif (self.devType == HUMIDITY_DEVICE_TYPE):
            self.execHumidityCmd()
        elif (self.devType == LIGHTSENSOR_DEVICE_TYPE):
            self.execLightSensorCmd()
        elif (self.devType == OCCUPANCY_DEVICE_TYPE):
            self.execOccupancyCmd()
        elif (self.devType == WINDOWCOVERING_DEVICE_TYPE):
            self.execWindowCoveringCmd()
        elif (self.devType == ONOFFPLUGIN_DEVICE_TYPE):
            self.execOnOffPluginCmd()
        else:
            print('ERROR: Unknown cmd')

    def execLightBulbCmd(self):
        print('execLightBulbCmd' + ' : ' + self.devNum)
        lightCmd = CommandUtil.get_command_list_by_device_type(
            LIGHTBULB_DEVICE_TYPE)
        if (self.cmd == lightCmd[self.CMD_1]['Name']):
            if self.cmdVal in lightCmd[self.CMD_1]['val']:
                state = True if self.cmdVal == lightCmd[self.CMD_1]['val'][0] else False
                LightCommand.onOff(self.devNum, state)
                print('On' if state else 'Off')
            else:
                print('ERROR: Unknown value')
        elif (self.cmd == lightCmd[self.CMD_2]['Name']):
            print('Level Control : ' + self.cmdVal)
            # value = (int(self.cmdVal)*254)/100
            LightCommand.dimming(self.devNum, self.cmdVal)
        elif (self.cmd == lightCmd[self.CMD_3]['Name']):
            print('Color Control : ' + self.cmdVal)
            # value = int(round(1000000/int(self.cmdVal), 0))
            LightCommand.colortemp(self.devNum, self.cmdVal)
        else:
            print('ERROR: Unknown Command')

    def execDoorLockCmd(self):
        print('execDoorLockCmd' + ' : ' + self.devNum)
        doorLockCmd = CommandUtil.get_command_list_by_device_type(
            DOORLOCK_DEVICE_TYPE)
        if (self.cmd == doorLockCmd[self.CMD_1]['Name']):
            if self.cmdVal in doorLockCmd[self.CMD_1]['val']:
                state = True if self.cmdVal == doorLockCmd[self.CMD_1]['val'][0] else False
                DoorlockCommand.lockUnlock(self.devNum, state)
                print('Lock' if state else 'UnLock')
            else:
                print('ERROR: Unknown value')
        else:
            print('ERROR: Unknown Command')

    def execContactSensorCmd(self):
        print('execContactSensorCmd' + ' : ' + self.devNum)
        contactSensorCmd = CommandUtil.get_command_list_by_device_type(
            CONTACTSENSOR_DEVICE_TYPE)
        if (self.cmd == contactSensorCmd[self.CMD_1]['Name']):
            if self.cmdVal in contactSensorCmd[self.CMD_1]['val']:
                state = True if self.cmdVal == contactSensorCmd[self.CMD_1]['val'][0] else False
                ContactSensorCommand.closeOpen(self.devNum, state)
                print('Close' if state else 'Open')
            else:
                print('ERROR: Unknown value')
        else:
            print('ERROR: Unknown Command')

    def execTemperatureCmd(self):
        print('execTemperatureCmd' + ' : ' + self.devNum)
        temperatureCmd = CommandUtil.get_command_list_by_device_type(
            TEMPERATURE_DEVICE_TYPE)
        if (self.cmd == temperatureCmd[self.CMD_1]['Name']):
            print('Level Control : ' + self.cmdVal)
            # value = int(self.cmdVal) * 100
            TempCommand.set_temp(self.devNum, self.cmdVal)

    def execHumidityCmd(self):
        print('execHumidityCmd' + ' : ' + self.devNum)
        humidityCmd = CommandUtil.get_command_list_by_device_type(
            HUMIDITY_DEVICE_TYPE)
        if (self.cmd == humidityCmd[self.CMD_1]['Name']):
            print('Level Control : ' + self.cmdVal)
            # value = (int(self.cmdVal)*10000)/100
            HumidCommand.set_humid(self.devNum, self.cmdVal)

    def execLightSensorCmd(self):
        print('execLightSensorCmd' + ' : ' + self.devNum)
        lightSensorCmd = CommandUtil.get_command_list_by_device_type(
            LIGHTSENSOR_DEVICE_TYPE)
        if (self.cmd == lightSensorCmd[self.CMD_1]['Name']):
            print('Level Control :' + self.cmdVal)
            # value = (10000 * math.log(int(self.cmdVal), 10)) + 1
            LightsensorCommand.set_lightsensor(self.devNum, self.cmdVal)

    def execOccupancyCmd(self):
        print('execOccupancyCmd' + ' : ' + self.devNum)
        occupancyCmd = CommandUtil.get_command_list_by_device_type(
            OCCUPANCY_DEVICE_TYPE)
        if (self.cmd == occupancyCmd[self.CMD_1]['Name']):
            if self.cmdVal in occupancyCmd[self.CMD_1]['val']:
                state = True if self.cmdVal == occupancyCmd[self.CMD_1]['val'][0] else False
                OccupancyCommand.occupiedUnoccupied(self.devNum, state)
                print('Occupied' if state else 'Unoccupied')
            else:
                print('ERROR: Unknown value')

    def execWindowCoveringCmd(self):
        print('execWindowCoveringCmd' + ' : ' + self.devNum)
        windowCoveringCmd = CommandUtil.get_command_list_by_device_type(
            WINDOWCOVERING_DEVICE_TYPE)
        if (self.cmd == windowCoveringCmd[self.CMD_1]['Name']):
            print('Level Control : ' + self.cmdVal)
            WindowCoveringCommand.set_target_position(self.devNum, self.cmdVal)

    def execOnOffPluginCmd(self):
        print('execOnOffPluginCmd' + ' : ' + self.devNum)
        OnOffPluginCmd = CommandUtil.get_command_list_by_device_type(
            ONOFFPLUGIN_DEVICE_TYPE)
        if (self.cmd == OnOffPluginCmd[self.CMD_1]['Name']):
            if self.cmdVal in OnOffPluginCmd[self.CMD_1]['val']:
                state = True if self.cmdVal == OnOffPluginCmd[self.CMD_1]['val'][0] else False
                OnOffPluginCommand.onOff(self.devNum, state)
                print('On' if state else 'Off')

    def __str__(self):
        return "devType:{1}, cmd:{2}, cmdVal:{3}, devNum:{1}".format(self.devType, self.cmd, self.cmdVal, self.devNum)


# ============================ ProcessCmd class   ========================================
class ProcessCmd(QThread):
    update_highlight = pyqtSignal(int)
    complete_autotest = pyqtSignal()
    # Class Variable
    mDevConfFilepath = 'src/automation/conf/'
    mScriptFilePath = 'src/automation/output/'

    # The init method or constructor
    def __init__(self, aUiObj, aFilePath):
        super().__init__()
        print('ProcessCmd init')
        self.uiObj = aUiObj
        self.scriptFilePath = aFilePath

        self.exec_stop = False
        self.count = 0

  # Total Cmd

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
        # Run Cmd

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
                            ExecuteCmd(child.get('devType'), child.get(
                                'cmdName'), child.get('val')).execCmd()
                            self.setSleep(1)
                    print('Current Loop Count->', curCnt)
                    curCnt += 1

                    self.setSleep(loopInterval)
                uiIdx += totalchild
                self.send_highlight(uiIdx)
                uiIdx += 1
            else:
                ExecuteCmd(element.get('devType'), element.get(
                    'cmdName'), element.get('val')).execCmd()
                self.send_highlight(uiIdx)
                uiIdx += 1
                self.setSleep(1)
        self.complete_autotest.emit()

    def setSleep(self, delaytime):
        count = 0
        while not self.exec_stop:
            if delaytime <= count:
                break
            QTest.qWait(1000)
            count += 1

    def send_highlight(self, pos):
        if not self.exec_stop:
            self.update_highlight.emit(pos)
            QTest.qWait(200)

    def stop(self):
        self.exec_stop = True
        self.quit()
        QTest.qWait(1000)
