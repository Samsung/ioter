from common.common_window import CommonWindow


class TestWindow(CommonWindow):
    def __init__(self, view_name, icon_name, device_info, parent, window_manager):
        super().__init__(view_name, icon_name, device_info, parent, window_manager)

    def power_onoff(self, state):
        self.pushButtonDevicePower.setText(
            {True: "Power Off", False: "Power On"}[state])
        if state:
            self.stackedWidget.setCurrentIndex(1)
            self.textBrowserLog.append("=== Matter Commissioning ===")
            self.device_info.set_commissioning_state(True)

        else:
            self.device_info.set_commissioning_state(True)
            self.stackedWidget.setCurrentIndex(2)
