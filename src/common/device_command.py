import os
import math

'''
* Device Commands Table
-----------------------------------------------------------------------------------
Device Type         | Device ID     | Commands
-----------------------------------------------------------------------------------
Light Bulb          | 269           | 'on', 'off', 'dimming', 'colortemp'
Door Lock           | 10            | 'lock', 'unlock'
Contact Sensor      | 21            | 'open', 'close'
Temperature         | 770           | 'set_temp'
Humidity            | 775           | 'set_humid'
Lightsensor         | 262           | 'set_lightsensor'
Occupancy           | 263           | 'occupied', 'unoccupied'
Windowcovering      | 514           | 'set_target_position', 'set_current_postion'
On Off Plugin       | 266(0x10A)    | 'on', 'off'
-----------------------------------------------------------------------------------
'''
LIGHTBULB_DEVICE_TYPE = 'Light Bulb'
LIGHTBULB_DEVICE_ID = '268'
LIGHTBULB_DIM_MIN_VAL = 0
LIGHTBULB_DIM_MAX_VAL = 100
LIGHTBULB_DIM_DEFAULT = 100
LIGHTBULB_DIM_ST_CONVERT = 254
LIGHTBULB_COLOR_TEMP_MIN_VAL = 2000
LIGHTBULB_COLOR_TEMP_MAX_VAL = 12000
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


class ForceClose():
    ALL = int('0b1110', 2)
    AUTOMATION = int('0b1000', 2)
    AUTO_ONBOARDING = int('0b0100', 2)
    DEVICES = int('0b0010', 2)


class Command():
    def _return_light_bulb_command():
        command1 = {
            "Name": "On/Off",
            "val": ['On', 'Off']
        }
        command2 = {
            "Name": "Level Control %",
            "range": [LIGHTBULB_DIM_MIN_VAL, LIGHTBULB_DIM_MAX_VAL]
        }
        command3 = {
            "Name": "Color Control K",
            "range": [LIGHTBULB_COLOR_TEMP_MIN_VAL, LIGHTBULB_COLOR_TEMP_MAX_VAL]
        }
        return [command1, command2, command3]

    def _return_doorlock_command():
        command1 = {
            "Name": "Lock/UnLock",
            "val": ['Lock', 'UnLock']
        }
        return [command1]

    def _return_contact_sensor_command():
        command1 = {
            "Name": "Open/Close",
            "val": ['Close', 'Open']
        }
        return [command1]

    def _return_temp_sensor_command():
        command1 = {
            "Name": "Level Control °C",
            "range": [TEMPERATURE_MIN_VAL, TEMPERATURE_MAX_VAL]
        }
        return [command1]

    def _return_humid_sensor_command():
        command1 = {
            "Name": "Level Control %",
            "range": [HUMIDITY_MIN_VAL, int(HUMIDITY_MAX_VAL/100)]
        }
        return [command1]

    def _return_light_sensor_command():
        command1 = {
            "Name": "Level Control lux",
            "range": [LIGHTSENSOR_MIN_VAL, LIGHTSENSOR_MAX_VAL]
        }
        return [command1]

    def _return_occupancy_sensor_command():
        command1 = {
            "Name": "Occupied/Unoccupied",
            "val": ['Occupied', 'Unoccupied']
        }
        return [command1]

    def _return_window_covering_command():
        command1 = {
            "Name": "Level Control %",
            "range": [0, 100]
        }
        return [command1]

    def _return_onoff_plugin_command():
        command1 = {
            "Name": "On/Off",
            "val": ['On', 'Off']
        }
        return [command1]


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

    device_id_command = {
        LIGHTBULB_DEVICE_ID: Command._return_light_bulb_command(),
        DOORLOCK_DEVICE_ID: Command._return_doorlock_command(),
        CONTACTSENSOR_DEVICE_ID: Command._return_contact_sensor_command(),
        TEMPERATURE_DEVICE_ID: Command._return_temp_sensor_command(),
        HUMIDITY_DEVICE_ID: Command._return_humid_sensor_command(),
        LIGHTSENSOR_DEVICE_ID: Command._return_light_sensor_command(),
        OCCUPANCY_DEVICE_ID: Command._return_occupancy_sensor_command(),
        WINDOWCOVERING_DEVICE_ID: Command._return_window_covering_command(),
        ONOFFPLUGIN_DEVICE_ID: Command._return_onoff_plugin_command()
    }

    def get_supported_device_type():
        return CommandUtil.device_type_id

    def get_command_list_by_device_type(device_type):
        device_id = CommandUtil.device_type_id.get(device_type, '')
        return CommandUtil.get_command_list_by_device_id(device_id)

    def get_command_list_by_device_id(device_id):
        return CommandUtil.device_id_command.get(device_id, [])

    def get_device_id_by_device_type(device_type):
        return CommandUtil.device_type_id.get(device_type, '')

    def get_device_type_by_device_id(device_id):
        keys = [key for key, value in CommandUtil.device_type_id.items()
                if value == device_id]
        if keys:
            return keys[0]
        return None


class PowerCommand():
    def off(device_num):
        power_command = "echo '{\"Name\":\"PowerOff\",\"onoff\":0}' > /tmp/chip_all_clusters_fifo_device"
        command = power_command + device_num
        os.popen(command)


'''
Light
'''
class LightCommand():
    def onOff(device_num, state):
        if state:
            value = 1  # On
        else:
            value = 0  # Off
        light_onoff_command = "echo '{\"Name\":\"Onoff\",\"onoff\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = light_onoff_command % (value, device_num)
        os.popen(command)

    def dimming(device_num, level):
        value = int(int(level)*LIGHTBULB_DIM_ST_CONVERT /
                    100)    # 0 < value < 254
        light_level_command = "echo '{\"Name\":\"Level\",\"level\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = light_level_command % (value, device_num)
        os.popen(command)

    def colortemp(device_num, level):
        value = int(round(1000000/int(level), 0))   # 2000 < value < 10000
        print(f'value {value}')
        colortemp_command = "echo '{\"Name\":\"Colortemp\",\"colortemp\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = colortemp_command % (value, device_num)
        os.popen(command)


'''
Doorlock
'''
class DoorlockCommand():
    @staticmethod
    def lockUnlock(device_num, state):
        if state:
            value = 1  # Lock
        else:
            value = 2  # Unlock
        lock_command = "echo '{\"Name\":\"Lockstate\",\"lockstate\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = lock_command % (value, device_num)
        os.popen(command)


'''
ContactSensor
'''
class ContactSensorCommand():
    @staticmethod
    def closeOpen(device_num, state):
        if state:
            value = 1  # Close
        else:
            value = 0  # Open
        # ui reflect
        command = "echo bool:%s > /tmp/chip_pipe_device%s" % (
            value, device_num)
        os.popen(command)

        close_command = "echo '{\"Name\":\"Bool\",\"bool\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = close_command % (value, device_num)
        os.popen(command)


'''
Temperature
'''
class TempCommand():
    @staticmethod
    def set_temp(device_num, level):
        value = int(float(level) * 100)    # -27315 < value < 32767
        # ui reflect
        command = "echo temp:%s > /tmp/chip_pipe_device%s" % (
            value, device_num)
        os.popen(command)

        set_temp_command = "echo '{\"Name\":\"Measurement\",\"temp\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = set_temp_command % (value, device_num)
        os.popen(command)


'''
Humidity
'''
class HumidCommand():
    @staticmethod
    def set_humid(device_num, level):
        value = int(float(level) * 100)     # 0 < value < 10000
        # ui reflect
        command = "echo humid:%s > /tmp/chip_pipe_device%s" % (
            value, device_num)
        os.popen(command)

        set_humid_command = "echo '{\"Name\":\"Measurement\",\"humid\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = set_humid_command % (value, device_num)
        os.popen(command)


'''
LightSensor
'''
class LightsensorCommand():
    @staticmethod
    def set_lightsensor(device_num, measured_value):
        # ui reflect
        command = "echo illum:%s > /tmp/chip_pipe_device%s" % (measured_value, device_num)
        os.popen(command)

        set_measured_value_command = "echo '{\"Name\":\"Measurement\",\"illum\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = set_measured_value_command % (measured_value, device_num)
        os.popen(command)


'''
OccupancySensor
'''
class OccupancyCommand():
    @staticmethod
    def occupiedUnoccupied(device_num, state):
        if state:
            value = 1    # Occupied
        else:
            value = 0    # Unoccupid
        # ui reflect
        command = "echo occupancy:%s > /tmp/chip_pipe_device%s" % (
            value, device_num)
        os.popen(command)

        occupied_command = "echo '{\"Name\":\"Occupancy\",\"occupancy\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = occupied_command % (value, device_num)
        os.popen(command)


'''
WindowCovering
'''
class WindowCoveringCommand():
    @staticmethod
    def set_target_position(device_num, pos):
        value = 10000 - (int(pos) * 100)
        target_position_command = "echo '{\"Name\":\"WindowCovering\",\"target_position\":%s}' > /tmp/chip_all_clusters_fifo_device"
        command = (target_position_command % (value)) + device_num
        os.popen(command)

    @staticmethod
    def set_current_postion(device_num, pos):
        value = 10000 - (int(pos) * 100)
        current_position_command = "echo '{\"Name\":\"WindowCovering\",\"current_position\":%s}' > /tmp/chip_all_clusters_fifo_device"
        command = (current_position_command % (value)) + device_num
        os.popen(command)


'''
On Off Plugin
'''
class OnOffPluginCommand():
    def onOff(device_num, state):
        if state:
            value = 1  # On
        else:
            value = 0  # Off
        plug_on_command = "echo '{\"Name\":\"Onoff\",\"onoff\":%s}' > /tmp/chip_all_clusters_fifo_device%s"
        command = plug_on_command % (value, device_num)
        os.popen(command)
