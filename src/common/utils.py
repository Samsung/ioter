import os
import sys
import psutil
import qrcode
from pathlib import Path
from PyQt5.QtGui import *
from random import Random


class Utils():
    def get_base_path():
        util_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(util_path, "../../")
        return getattr(sys, "_MEIPASS", base_path)


    def get_absolute_path(relative_path):
        return os.path.join(Utils.get_base_path(), relative_path)

    def remove_files(dir_path, file_name):
        # ex. Utils.remove_files('/tmp', 'chip_*')
        for p in Path(dir_path).glob(file_name):
            p.unlink()

    def get_res_path():
        return os.path.join(Utils.get_base_path(), "res/")

    def get_icon_path(file_name):
        return os.path.join(Utils.get_res_path(), "icon/" + file_name)

    def get_view_path(file_name):
        return os.path.join(Utils.get_res_path(), "view/" + file_name)

    def get_tmp_path():
        return os.path.join(Utils.get_base_path(), "tmp/")

    def get_screenshot_path():
        return os.path.join(Utils.get_res_path(), "screenshot/")

    def get_script_path():
        return os.path.join(Utils.get_base_path(), "script/")

    def get_automation_path():
        return os.path.join(Utils.get_base_path(), "src/automation/")

    def get_thread_lib_path():
        return os.path.join(Utils.get_base_path(), "lib/")

    def get_ioter_path():
        return os.path.join(Utils.get_base_path(), "bin/")

    def get_setup_code(code):
        setup_code = code.split(":")
        return setup_code[1]

    def get_thread_lib_prefix():
        return "libopenthread-cli.so."

    def get_ioter_prefix():
        return "chip-all-clusters-app-"

    def get_qrcode_img(qr_data, width, height):
        qr_path = os.path.join(Utils.get_tmp_path(), "qrcode.png")
        qr_data = qr_data.split(":", 1)
        qr_img = qrcode.make(qr_data[1])
        qr_img.save(qr_path)
        return Utils.get_icon_img(qr_path, width, height)

    def get_icon_img(file_path, width, height):
        icon_img = QPixmap(file_path)
        icon_img = icon_img.scaledToWidth(width)
        icon_img = icon_img.scaledToHeight(height)
        return icon_img

    def get_ui_style_toggle_btn(toggle):
        style_string = "background-color: %s;"\
            "font-weight: bold;"\
            "border-radius: 3px;"\
            "border: 1px solid %s;"\
            "color: %s"
        if toggle:
            style = style_string % (
                "white", "rgb(186, 186, 186)", "rgb(58, 134, 255)")
        else:
            style = style_string % (
                "rgb(58, 134, 255)", "rgb(58, 134, 255)", "white")
        return style

    def isnumeric(s_data):
        arr = s_data.split(".", maxsplit=1)
        for item in arr:
            print("isnumeric item val : " + item)
            if not item.isnumeric():
                return False
        return True

    def remove_matter_files(device_num):
        Utils.remove_files('/tmp', 'chip_*' + 'device' + str(device_num) + "*")

    def remove_thread_setting_file(thread_setting_file):
        Utils.remove_files(Utils.get_tmp_path(), thread_setting_file)

    def killChildren(pid):
        if pid == -1:
            print(
                "Don't need to terminate process tree because current pid is invalid (-1)")
            return

        print("terminateProcessTree : starting pid : " + str(pid))
        parent = psutil.Process(pid)
        for child in parent.children(True):
            try:
                if child.is_running():
                    # print("try to terminate ", child.pid)
                    child.terminate()
            except Exception as e:
                print("exception : ", e)

    def generate_random_discriminator():
        seed = None
        supported_apis = dir(os)
        if 'uname' in supported_apis:
            seed = os.uname()
        elif 'getlogin' in supported_apis:
            seed = os.getlogin()
        if seed is None:
            rand = Random()
        else:
            rand = Random(str(seed))
        return rand.randint(0x3E8, 0xFFF)


def singleton(cls_):
    class class_w(cls_):
        _instance = None
        _sealed = False

        def __new__(cls_, *args, **kwargs):

            if class_w._instance is None:
                class_w._instance = super(class_w, cls_).__new__(cls_)
                class_w._instance._sealed = False
            return class_w._instance

        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super(class_w, self).__init__(*args, **kwargs)
            self._sealed = True
    class_w.__name__ = cls_.__name__
    return class_w
