from common.utils import Utils
from common.device_command import CommandUtil

import os
import time
from PyQt5.QtWidgets import *
# from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import *
from com.dtmilano.android.viewclient import ViewClient
# from com.dtmilano.android.adb.adbclient import AdbClient

ONBOARDING_TIMEOUT = 600
REMOVING_TIMEOUT = 120
# start onboarding
ONBOARDING_ADD_BUTTON = 0
ONBOARDING_ADDITIONAL_ADD_BUTTON = 1
ONBOARDING_MANUAL_PAIRING_CODE_BOTTON = 2
ONBOARDING_MANUAL_PAIRING_CODE_TEXTBOX = 3
ONBOARDING_MANUAL_PAIRING_CODE_INPUT_DONE = 4
ONBOARDING_CONTINUE_BUTTON = 5
ONBOARDING_NO_MATTER_CERT_DEVICE_SKIP_BUTTON = 6
ONBOARDING_MATTER_DEVICE_NAME_CHANGE = 7
ONBOARDING_MATTER_DEVICE_NAME_CHANGE_DONE = 8
ONBOARDING_DONE_BACK_TO_FIRST_SCREEN = 9
# remove device
REMOVE_START = 30
REMOVE_BUTTON = 31
REMOVE_DONE = 32
# error capture
ERROR_CHECK_LAYOUT = 40
# words
ERROR_OCCUR_KOR = 90
ERROR_OCCUR_ENG = 91
ADD_DEVICE_KOR = 92
ADD_DEVICE_ENG = 93
REMOVE_BUTTON_KOR = 94
REMOVE_BUTTON_ENG = 95
ONBOARDING_SUCCESS = 1
ONBOARDING_FAILURE = 0
REMOVING_SUCCESS = 3
REMOVING_FAILURE = 2

dev_prefix = "IoTer Device"
debug = 0


class autoDevice(QThread):
    update_onboarding_state = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.device, self.serialno = ViewClient.connectToDeviceOrExit()
        self.vc = ViewClient(self.device, self.serialno)

    def run(self):
        self.device_name = f"{CommandUtil.get_device_type_by_device_id(self.parent.device_info.device_id)}-{self.parent.device_info.device_num}"
        self.count = 0
        if self.auto_onboarding():
            print("onboarding success!")
            self.update_onboarding_state.emit(ONBOARDING_SUCCESS)
            self.vc.sleep(1)
        else:
            print("onboarding failed..")
            self.update_onboarding_state.emit(ONBOARDING_FAILURE)
            self.vc.sleep(1)

    def auto_onboarding(self):
        start_time = time.time()
        stair = ONBOARDING_ADD_BUTTON
        while True:
            obj = self.vc.findViewById(self.get_smartthings_view_id(stair))
            if obj and stair == ONBOARDING_ADDITIONAL_ADD_BUTTON:
                if obj.getText() == self.get_smartthings_view_id(ADD_DEVICE_KOR) or\
                        obj.getText() == self.get_smartthings_view_id(ADD_DEVICE_ENG):
                    if debug == 1:
                        print(
                            f"stair::ONBOARDING_ADDITIONAL_ADD_BUTTON, obj={obj}")
                    obj.touch()
                    stair += 1
            elif not obj and stair == ONBOARDING_ADDITIONAL_ADD_BUTTON:
                self.vc.dump(window=-1)
                obj = self.vc.findViewById(self.get_smartthings_view_id(stair))
                if obj:
                    if debug == 1:
                        print(
                            f"stair::ONBOARDING_ADDITIONAL_ADD_BUTTON, obj={obj}")
                    obj.touch()
                    stair += 1
                else:
                    obj = self.vc.findViewById(self.get_smartthings_view_id(
                        ONBOARDING_MANUAL_PAIRING_CODE_BOTTON))
                    if obj:
                        if debug == 1:
                            print(
                                f"stair::ONBOARDING_MANUAL_PAIRING_CODE_BOTTON, obj={obj}")
                        obj.touch()
                        stair += 2
            elif obj and stair == ONBOARDING_MANUAL_PAIRING_CODE_TEXTBOX:
                if debug == 1:
                    print(
                        f"stair::ONBOARDING_MANUAL_PAIRING_CODE_TEXTBOX, obj={obj}")
                obj.type(self.parent.plainTextEditPairingCode.toPlainText())
                stair += 1
            elif obj and stair == ONBOARDING_MATTER_DEVICE_NAME_CHANGE:
                if debug == 1:
                    print(
                        f"stair::ONBOARDING_MATTER_DEVICE_NAME_CHANGE, obj={obj}")
                obj.setText(self.device_name)
                stair += 1
            elif obj and stair == ONBOARDING_MATTER_DEVICE_NAME_CHANGE_DONE:
                if debug == 1:
                    print(
                        f"stair::ONBOARDING_MATTER_DEVICE_NAME_CHANGE_DONE, obj={obj}")
                if self.device.isKeyboardShown():
                    self.device.press("BACK")
                    if debug == 1:
                        print(
                            f"stair::ONBOARDING_MATTER_DEVICE_NAME_CHANGE_DONE, keyboard down")
                    time.sleep(2)
                obj.touch()
                time.sleep(12)
                stair += 1
            elif stair == ONBOARDING_DONE_BACK_TO_FIRST_SCREEN:
                if debug == 1:
                    print("stair::ONBOARDING_DONE_BACK_TO_FIRST_SCREEN")
                self.vc.dump(window=-1)
                obj = self.vc.findViewWithText(self.device_name)
                if obj or self.count >= 3:
                    if debug == 1:
                        print(f"obj={obj}")
                    self.vc.device.press("BACK")
                    time.sleep(3)
                    if debug == 1:
                        print("press BACK")
                    return True
                else:
                    if debug == 1:
                        print(
                            f"stair::ONBOARDING_DONE_BACK_TO_FIRST_SCREEN {self.device_name} not found")
                    self.count += 1
            elif obj:
                if debug == 1:
                    print(f"stair::{stair}, obj={obj}")
                obj.touch()
                time.sleep(1)
                stair += 1
            elif not obj:
                if stair == ONBOARDING_MATTER_DEVICE_NAME_CHANGE:
                    if debug == 1:
                        print("waiting download plugin in SmartThings...")
                    self.vc.dump(window=-1, sleep=5)
                else:
                    if debug == 1:
                        print(f"not found stair::{stair}'s obj")
                    self.vc.dump(window=-1)

            # screenshot when error occurs
            err = self.vc.findViewById(
                self.get_smartthings_view_id(ERROR_CHECK_LAYOUT))
            if err:
                if err.getText() == self.get_smartthings_view_id(ERROR_OCCUR_KOR) or\
                   err.getText() == self.get_smartthings_view_id(ERROR_OCCUR_ENG):
                    if debug == 1:
                        print(err)
                    self.screenshot()
                    err2 = self.vc.findViewById(self.get_smartthings_view_id(
                        ONBOARDING_MATTER_DEVICE_NAME_CHANGE_DONE))
                    err2.touch()
                    time.sleep(1)
                    self.vc.device.press("BACK")
                    if debug == 1:
                        print("press BACK")
                    return False

            # screenshot when too much delay occurred during onboarding and return error
            now_time = time.time()
            if now_time - start_time > ONBOARDING_TIMEOUT:
                print(
                    f"Too much time {ONBOARDING_TIMEOUT}s goes on for onboarding... it is failed!")
                self.vc.device.press("BACK")
                while True:
                    self.vc.dump(window=-1)
                    ti = self.vc.findViewById(
                        self.get_smartthings_view_id(ERROR_CHECK_LAYOUT))
                    if ti:
                        self.screenshot()
                        if debug == 1:
                            print(ti)
                        ti.touch()
                        break
                time.sleep(1)
                self.vc.device.press("BACK")
                time.sleep(1)
                if debug == 1:
                    print("press BACK")
                return False

    def auto_remove_device(self):
        if self.remove_device():
            print("removing success!")
            self.update_onboarding_state.emit(REMOVING_SUCCESS)
            self.vc.sleep(1)
        else:
            print("removing failed!")
            self.update_onboarding_state.emit(REMOVING_FAILURE)
            self.vc.sleep(1)

    def remove_device(self):
        print(f"{self.device_name} will be removed ...")
        start_time = time.time()
        stair = REMOVE_START
        while True:
            if stair == REMOVE_START:
                self.vc.dump(window=-1)
                obj = self.vc.findViewWithText(self.device_name)
                if obj:
                    if debug == 1:
                        print(obj)
                    (x, y) = obj.getCenter()
                    self.device.drag((x, y), (x, y), 2000, 1)
                    stair = stair + 1
                else:
                    print(f"can't find {self.device_name}")
                    if time.time() - start_time > REMOVING_TIMEOUT:
                        print(f"can't not find {self.device_name} anymore")
                        return False
                    continue
            elif stair >= REMOVE_BUTTON and stair <= REMOVE_DONE:
                self.vc.dump(window=-1)
                if stair == REMOVE_BUTTON:
                    obj = self.vc.findViewWithText(
                        self.get_smartthings_view_id(REMOVE_BUTTON_KOR))
                    if not obj:
                        obj = self.vc.findViewWithText(
                            self.get_smartthings_view_id(REMOVE_BUTTON_ENG))
                else:
                    obj = self.vc.findViewById(
                        self.get_smartthings_view_id(stair))
                if obj:
                    if debug == 1:
                        print(obj)
                    obj.touch()
                    stair = stair + 1
                else:
                    if stair == REMOVE_BUTTON:
                        print(f"can't not find edit button")
                    elif stair == REMOVE_DONE:
                        print(f"can't find remove device button")
                    continue
            else:
                print("exit removing device")
                return True

    def screenshot(self):
        screenshot_path = Utils.get_screenshot_path()
        if not os.path.isdir(screenshot_path):
            os.mkdir(screenshot_path)
        self.vc.dump(window=-1)
        self.device.takeSnapshot(reconnect=True).save(
            f"{screenshot_path}error_{self.device_name}_{time.strftime('%Y_%m_%d-%H_%M_%S')}.png", "PNG")
        print("error screenshot done")

    def get_smartthings_view_id(self, key):
        type = {
            ONBOARDING_ADD_BUTTON: "com.samsung.android.oneconnect:id/add_menu_button",
            ONBOARDING_ADDITIONAL_ADD_BUTTON: "com.samsung.android.oneconnect:id/title",
            ONBOARDING_MANUAL_PAIRING_CODE_BOTTON: "com.samsung.android.oneconnect:id/enter_setup_code_button",
            ONBOARDING_MANUAL_PAIRING_CODE_TEXTBOX: "com.samsung.android.oneconnect:id/add_device_item_serial_edit_text",
            ONBOARDING_MANUAL_PAIRING_CODE_INPUT_DONE: "com.samsung.android.oneconnect:id/menu_done",
            ONBOARDING_CONTINUE_BUTTON: "com.samsung.android.oneconnect:id/onboarding_item_main_button",
            ONBOARDING_NO_MATTER_CERT_DEVICE_SKIP_BUTTON: "android:id/button1",
            ONBOARDING_MATTER_DEVICE_NAME_CHANGE: "com.samsung.android.oneconnect:id/onboarding_success_card_detail_view_editor",
            ONBOARDING_MATTER_DEVICE_NAME_CHANGE_DONE: "com.samsung.android.oneconnect:id/onboarding_item_positive_navigation_text",
            ONBOARDING_DONE_BACK_TO_FIRST_SCREEN: "android.widget.Button",\
            # REMOVE_BUTTON:"id/no_id/5",\
            REMOVE_BUTTON_ENG: "Remove",\
            REMOVE_DONE: "android:id/button1",\
            REMOVE_BUTTON_KOR: "삭제",\
            ERROR_CHECK_LAYOUT: "com.samsung.android.oneconnect:id/onboarding_step_description_layout",\
            ERROR_OCCUR_KOR: "오류가 있어요",\
            ERROR_OCCUR_ENG: "Something went wrong",\
            ADD_DEVICE_KOR: "기기 추가",\
            ADD_DEVICE_ENG: "Add device"
        }.get(key, 0)
        return type

    def stop(self):
        self.quit()
        self.wait(1000)
