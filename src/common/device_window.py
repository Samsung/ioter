from common.device_command import *
from common.common_window import CommonWindow
from common.test_window import TestWindow
from things.light import LightWindow
from things.doorlock import DoorlockWindow
from things.contact import ContactWindow
from things.doorlock import DoorlockWindow
from things.temperature import TempWindow
from things.humidity import HumidWindow
from things.lightsensor import LightsensorWindow
from things.occupancy import OccupancyWindow
from things.windowcovering import WindowcoveringWindow
from things.plugin_onoff import OnoffPlugin


def get_device_window_by_device_type(device_type, device_info, use_test_window, window_manager):
    window_class = CommonWindow if not use_test_window else TestWindow
    window = {
        LIGHTBULB_DEVICE_TYPE: lambda device_info: LightWindow(device_info, window_class, window_manager),
        DOORLOCK_DEVICE_TYPE: lambda device_info: DoorlockWindow(device_info, window_class, window_manager),
        CONTACTSENSOR_DEVICE_TYPE: lambda device_info: ContactWindow(device_info, window_class, window_manager),
        TEMPERATURE_DEVICE_TYPE: lambda device_info: TempWindow(device_info, window_class, window_manager),
        HUMIDITY_DEVICE_TYPE: lambda device_info: HumidWindow(device_info, window_class, window_manager),
        LIGHTSENSOR_DEVICE_TYPE: lambda device_info: LightsensorWindow(device_info, window_class, window_manager),
        OCCUPANCY_DEVICE_TYPE: lambda device_info: OccupancyWindow(device_info, window_class, window_manager),
        WINDOWCOVERING_DEVICE_TYPE: lambda device_info: WindowcoveringWindow(
            device_info, window_class, window_manager),
        ONOFFPLUGIN_DEVICE_TYPE: lambda device_info: OnoffPlugin(
            device_info, window_class, window_manager)
    }
    return window.get(device_type, None)(device_info)
