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
# File : device_command.py
# Description: Device commands and operations
import os


# Device Commands Table
# -----------------------------------------------------------------------------------
# Device Type         | Device ID     | Commands
# -----------------------------------------------------------------------------------
# Light Bulb          | 269           | 'on', 'off', 'dimming', 'colortemp'
# Door Lock           | 10            | 'lock', 'unlock'
# Contact Sensor      | 21            | 'open', 'close'
# Temperature         | 770           | 'set_temp'
# Humidity            | 775           | 'set_humid'
# Lightsensor         | 262           | 'set_lightsensor'
# Occupancy           | 263           | 'occupied', 'unoccupied'
# Windowcovering      | 514           | 'set_target_position', 'set_current_postion'
# On Off Plugin       | 266(0x10A)    | 'on', 'off'
# -----------------------------------------------------------------------------------

LIGHTBULB_DEVICE_TYPE = 'Light Bulb'
LIGHTBULB_DEVICE_ID = '268'
LIGHTBULB_DIM_MIN_VAL = 0
LIGHTBULB_DIM_MAX_VAL = 100
LIGHTBULB_DIM_DEFAULT = 100
LIGHTBULB_DIM_ST_CONVERT = 254
LIGHTBULB_COLOR_TEMP_MIN_VAL = 1
LIGHTBULB_COLOR_TEMP_MAX_VAL = 65279
LIGHTBULB_COLOR_TEMP_DEFAULT = 4000
LIGHTBULB_DIM_UNIT = '%'
LIGHTBULB_COLOR_TEMP_UNIT = 'K'

DOORLOCK_DEVICE_TYPE = 'Door Lock'
DOORLOCK_DEVICE_ID = '10'
CONTACTSENSOR_DEVICE_TYPE = 'Contact Sensor'
CONTACTSENSOR_DEVICE_ID = '21'

TEMPERATURE_DEVICE_TYPE = 'Temperature'
TEMPERATURE_DEVICE_ID = '770'
TEMPERATURE_MIN_VAL = -273.15
TEMPERATURE_MAX_VAL = 327.67
TEMPERATURE_UNIT = '°C'

HUMIDITY_DEVICE_TYPE = 'Humidity'
HUMIDITY_DEVICE_ID = '775'
HUMIDITY_MIN_VAL = 0
HUMIDITY_MAX_VAL = 10000
HUMIDITY_UNIT = '%'

LIGHTSENSOR_DEVICE_TYPE = 'Light Sensor'
LIGHTSENSOR_DEVICE_ID = '262'
LIGHTSENSOR_MIN_VAL = 1
LIGHTSENSOR_MAX_VAL = 3576000
MEASURED_VALUE_MIN = 1
MEASURED_VALUE_MAX = 65534
LIGHTSENSOR_UNIT = ' lux'

OCCUPANCY_DEVICE_TYPE = 'Occupancy'
OCCUPANCY_DEVICE_ID = '263'
ONOFFPLUGIN_DEVICE_TYPE = 'OnOff Plugin'
ONOFFPLUGIN_DEVICE_ID = '266'

WINDOWCOVERING_DEVICE_TYPE = 'Windowcovering'
WINDOWCOVERING_DEVICE_ID = '514'
# 0 (close) --------- 100 (open)
WINDOWCOVERING_MIN_VAL = 0
WINDOWCOVERING_MAX_VAL = 100
WINDOWCOVERING_UNIT = "%"

BATTERY_MIN_VAL = 0
BATTERY_MAX_VAL = 100
BATTERY_UNIT = "%"

## Force close class ##
class ForceClose():
    ALL = int('0b1110', 2)
    AUTOMATION = int('0b1000', 2)
    AUTO_ONBOARDING = int('0b0100', 2)
    DEVICES = int('0b0010', 2)

## Commands utility class ##
class CommandUtil():
    device_type_id = {
        LIGHTBULB_DEVICE_TYPE: LIGHTBULB_DEVICE_ID,
        DOORLOCK_DEVICE_TYPE: DOORLOCK_DEVICE_ID,
        CONTACTSENSOR_DEVICE_TYPE: CONTACTSENSOR_DEVICE_ID,
        TEMPERATURE_DEVICE_TYPE: TEMPERATURE_DEVICE_ID,
        HUMIDITY_DEVICE_TYPE: HUMIDITY_DEVICE_ID,
        LIGHTSENSOR_DEVICE_TYPE: LIGHTSENSOR_DEVICE_ID,
        OCCUPANCY_DEVICE_TYPE: OCCUPANCY_DEVICE_ID,
        WINDOWCOVERING_DEVICE_TYPE: WINDOWCOVERING_DEVICE_ID,
        ONOFFPLUGIN_DEVICE_TYPE: ONOFFPLUGIN_DEVICE_ID
    }

    ## Get supported device types list ##
    def get_supported_device_type():
        return CommandUtil.device_type_id

    ## Get device id by device type ##
    def get_device_id_by_device_type(device_type):
        return CommandUtil.device_type_id.get(device_type, '')

    ## Get device type by device id ##
    def get_device_type_by_device_id(device_id):
        keys = [key for key, value in CommandUtil.device_type_id.items()
                if value == device_id]
        if keys:
            return keys[0]
        return None


## Power command class ##
class PowerCommand():
    ## Device off command ##
    def off(device_num):
        power_command = "echo '{\"Name\":\"PowerOff\",\"onoff\":0}' > /tmp/chip_all_clusters_fifo_device"
        command = power_command + device_num
        os.popen(command)

## Battery command class ##
class BatteryCommand():
    ## Battery remain command ##
    def remain(device_num, value):
        battery_command = "echo '{\"Name\":\"BatPercent\",\"remain\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = battery_command % (value, device_num)
        os.popen(command)

## Light commands set operation ##
class LightCommand():
    ## Set on/off ##
    def onOff(device_num, state):
        if state:
            value = 1  # On
        else:
            value = 0  # Off

        light_onoff_command = "echo '{\"Name\":\"Onoff\",\"onoff\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = light_onoff_command % (value, device_num)
        os.popen(command)

    ## Set dimming ##
    def dimming(device_num, level):
        value = int(int(level)*LIGHTBULB_DIM_ST_CONVERT /
                    100)    # 0 < value < 254

        light_level_command = "echo '{\"Name\":\"Level\",\"level\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = light_level_command % (value, device_num)
        os.popen(command)

    ## Set color tempareture ##
    def colortemp(device_num, level):
        value = int(round(1000000/int(level), 0))   # 1 < value < 65279

        colortemp_command = "echo '{\"Name\":\"Colortemp\",\"colortemp\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = colortemp_command % (value, device_num)
        os.popen(command)

## Door lock commands set operation ##
class DoorlockCommand():
    ## Set lock/unlock ##
    @staticmethod
    def lockUnlock(device_num, state):
        if state:
            value = 1  # Lock
        else:
            value = 2  # Unlock

        lock_command = "echo '{\"Name\":\"Lockstate\",\"lockstate\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = lock_command % (value, device_num)
        os.popen(command)

## Contact Sensor commands set operation ##
class ContactSensorCommand():
    ## Set close/open ##
    @staticmethod
    def closeOpen(device_num, state):
        if state:
            value = 1  # Close
        else:
            value = 0  # Open

        close_command = "echo '{\"Name\":\"Bool\",\"bool\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = close_command % (value, device_num)
        os.popen(command)

## Temperature commands set operation ##
class TempCommand():
    ## Set temperature ##
    @staticmethod
    def set_temp(device_num, level):
        value = int(float(level) * 100)    # -27315 < value < 32767

        set_temp_command = "echo '{\"Name\":\"Measurement\",\"temp\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = set_temp_command % (value, device_num)
        os.popen(command)

## Humidity commands set operation ##
class HumidCommand():
    ## Set humidity ##
    @staticmethod
    def set_humid(device_num, level):
        value = int(float(level) * 100)     # 0 < value < 10000

        set_humid_command = "echo '{\"Name\":\"Measurement\",\"humid\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = set_humid_command % (value, device_num)
        os.popen(command)

## Light Sensor commands set operation ##
class LightsensorCommand():
    ## Set Lux ##
    @staticmethod
    def set_lightsensor(device_num, measured_value):

        set_measured_value_command = "echo '{\"Name\":\"Measurement\",\"illum\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = set_measured_value_command % (measured_value, device_num)
        os.popen(command)

## Occupancy Sensor commands set operation ##
class OccupancyCommand():
    ## Set Occupied/Unoccupid ##
    @staticmethod
    def occupiedUnoccupied(device_num, state):
        if state:
            value = 1    # Occupied
        else:
            value = 0    # Unoccupid

        occupied_command = "echo '{\"Name\":\"Occupancy\",\"occupancy\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = occupied_command % (value, device_num)
        os.popen(command)

## Window covering commands set operation ##
class WindowCoveringCommand():
    ## Set target position ##
    @staticmethod
    def set_target_position(device_num, pos):
        value = 10000 - (int(pos) * 100)

        target_position_command = "echo '{\"Name\":\"WindowCovering\",\"target_position\":%s}' > /tmp/chip_all_clusters_fifo_device"
        command = (target_position_command % (value)) + device_num
        os.popen(command)

    ## Set current position ##
    @staticmethod
    def set_current_postion(device_num, pos):
        value = 10000 - (int(pos) * 100)

        current_position_command = "echo '{\"Name\":\"WindowCovering\",\"current_position\":%s}' > /tmp/chip_all_clusters_fifo_device"
        command = (current_position_command % (value)) + device_num
        os.popen(command)

## On off plugin commands set operation ##
class OnOffPluginCommand():
    ## Set On/off ##
    def onOff(device_num, state):
        if state:
            value = 1  # On
        else:
            value = 0  # Off

        plug_on_command = "echo '{\"Name\":\"Onoff\",\"onoff\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = plug_on_command % (value, device_num)
        os.popen(command)
