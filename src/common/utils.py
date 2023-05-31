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
# File : utils.py
# Description: Utilities APIs

import os
import sys
import psutil
import qrcode
import subprocess
from pathlib import Path
from PyQt5.QtGui import *
from random import Random

## Utility class ##
class Utils():
    ## Get base path ##
    def get_base_path():
        util_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(util_path, "../../")
        return getattr(sys, "_MEIPASS", base_path)

    ## Get absolute path ##
    def get_absolute_path(relative_path):
        return os.path.join(Utils.get_base_path(), relative_path)

    ## Remove files from path ##
    def remove_files(dir_path, file_name):
        # ex. Utils.remove_files('/tmp', 'chip_*')
        for p in Path(dir_path).glob(file_name):
            p.unlink()

    ## Get resource path ##
    def get_res_path():
        return os.path.join(Utils.get_base_path(), "res/")

    ## Get icon path ##
    def get_icon_path(file_name):
        return os.path.join(Utils.get_res_path(), "icon/" + file_name)

    ## Get UI files path ##
    def get_view_path(file_name):
        return os.path.join(Utils.get_res_path(), "view/" + file_name)

    ## Get tmp path ##
    def get_tmp_path():
        return os.path.join(Utils.get_base_path(), "tmp/")

    ## Get screenshot path ##
    def get_screenshot_path():
        return os.path.join(Utils.get_res_path(), "screenshot/")

    ## Get script path ##
    def get_script_path():
        return os.path.join(Utils.get_base_path(), "script/")

    ## Get OT thread library path ##
    def get_thread_lib_path():
        return os.path.join(Utils.get_base_path(), "lib/")

    ## Get ioter path ##
    def get_ioter_path():
        return os.path.join(Utils.get_base_path(), "bin/")

    ## Get source path ##
    def get_source_path():
        return os.path.join(Utils.get_base_path(), "src/")

    ## Get automation path ##
    def get_automation_path():
        return os.path.join(Utils.get_source_path(), "automation/")

    ## Get config path ##
    def get_config_path():
        return os.path.join(Utils.get_source_path(), "config.json")

    ## Get setup code ##
    def get_setup_code(code):
        setup_code = code.split(":")
        return setup_code[1]

    ## Get thread library prefix ##
    def get_thread_lib_prefix():
        return "libopenthread.so."

    ## Get ioter prefix ##
    def get_ioter_prefix():
        return "chip-all-clusters-app-"

    ## Get QRCode image ##
    def get_qrcode_img(qr_data, width, height):
        qr_path = os.path.join(Utils.get_tmp_path(), "qrcode.png")
        qr_data = qr_data.split(":", 1)
        qr_img = qrcode.make(qr_data[1])
        qr_img.save(qr_path)
        return Utils.get_icon_img(qr_path, width, height)

    ## Get icon image ##
    def get_icon_img(file_path, width, height):
        icon_img = QPixmap(file_path)
        icon_img = icon_img.scaledToWidth(width)
        icon_img = icon_img.scaledToHeight(height)
        return icon_img

    ## Verify if data is numeric ##
    def isnumeric(s_data):
        arr = s_data.split(".", maxsplit=1)
        for item in arr:
            print("isnumeric item val : " + item)
            if not item.isnumeric():
                return False
        return True

    ## Remove Data files ##
    def remove_data_files():
        Utils.remove_files('/tmp', 'chip_*')
        Utils.remove_files(Utils.get_tmp_path(), '0_*.data')

    ## Remove Matter files ##
    def remove_matter_files(device_num):
        Utils.remove_files('/tmp', 'chip_*' + 'device' + str(device_num) + "*")

    #3 Remove thread settings file ##
    def remove_thread_setting_file(thread_setting_file):
        Utils.remove_files(Utils.get_tmp_path(), thread_setting_file)

    ## Kill the child process ##
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

    ## Generate random discriminator ##
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

    ## Get ui style toggle button ##
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

    ## Get ui style slider ##
    def get_ui_style_slider(type):
        slider_stylesheet = """
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #eee, stop:1 #ccc);
                border: 1px solid #777;
                width: 14px;
                margin-top: -3px;
                margin-bottom: -3px;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fff, stop:1 #ddd);
                border: 1px solid #444;
            }
            """
        if type == "COMMON":
            addition = """
                QSlider::groove:horizontal {
                    background-color: rgba(58, 134, 255, 255);
                    border: 1px solid #bbb;
                    height: 10px;
                    border-radius: 4px;
                }
                QSlider::sub-page:horizontal {
                    background-color: rgba(58, 134, 255, 255);
                    border: 1px solid #bbb;
                    height: 10px;
                    border-radius: 4px;
                }
                QSlider::add-page:horizontal {
                    background-color: rgba(192, 191, 188, 255);
                    border: 1px solid #bbb;
                    height: 10px;
                    border-radius: 4px;
                }
                """
        elif type == "DIMMING":
            addition = """
                QSlider::groove:horizontal {
                    border: 1px solid #bbb;
                    background-color: qlineargradient(
                        spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, 
                        stop:0 rgba(26, 95, 180, 255), 
                        stop:0.485149 rgba(153, 193, 241, 255), 
                        stop:0.787129 rgba(246, 245, 244, 255), 
                        stop:1 rgba(255, 255, 255, 255));
                    height: 10px;
                    border-radius: 4px;
                }
                """
        elif type == "COLORTEMP":
            addition = """
                QSlider::groove:horizontal {
                    border: 1px solid #bbb;
                    background-color: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:0, 
                        stop:0 rgba(255, 138, 18, 255), 
                        stop:0.166 rgba(255, 196, 137, 255), 
                        stop:0.333 rgba(255, 228, 206, 255), 
                        stop:0.5 rgba(255, 249, 253, 255), 
                        stop:0.666 rgba(227, 233, 255, 255), 
                        stop:0.833 rgba(207, 218, 255, 255), 
                        stop:1 rgba(196, 209, 255, 255));
                    height: 10px;
                    border-radius: 4px;
                }
                """
        slider_stylesheet += addition
        return slider_stylesheet

    ## Get ioter version ##
    def get_version():
        ver = "UNKNOWN"
        try:
            ver = subprocess.check_output(['git', 'describe', '--tags']).decode()
        except:
            pass
        return ver

    # Add thread interface to routing table
    def add_route_with_device_num(device_num):
        interface = f"wpan{device_num}"
        priority = 256 - device_num
        command = f"sudo ip -6 route add default dev {interface} metric {priority}"
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Route added for {interface} with priority {priority}.")
        except subprocess.CalledProcessError as e:
            print("Error executing command:", e)


## Singleton ##
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
