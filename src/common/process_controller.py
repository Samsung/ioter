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
# File : process_controller.py
# Description: Control chip-all-cluster-app process

from common.utils import Utils

import signal
from psutil import *
from subprocess import *

## Process controller class ##
class ProcessController():
    RUN_PARAM_CHIP_ALL_CLUSTERS_FORMAT = \
    "--device-id %s --discriminator %s --thread "\
    "--thread-version %s --com-port %s "\
    "--thread-debug %s --device-num %s "\
    "--vendor-id %s --product-id %s "

    ## Init class ##
    def __init__(self):
        self.pid = -1

    ## Get PID ##
    def get_pid(self):
        # print("current pid : " + str(self.pid))
        return self.pid

    ## Set PID ##
    def set_pid(self, pid):
        print("PID change from " + str(self.pid) + " to " + str(pid))
        self.pid = pid

    ## Launch chip all clusters process ##
    def launch_chip_all_clusters(self, device_info):
        run_param = ProcessController.RUN_PARAM_CHIP_ALL_CLUSTERS_FORMAT % (
            device_info.device_id, device_info.discriminator,
            device_info.thread_type, device_info.com_port,
            device_info.debug_level, device_info.device_num,
            device_info.vid, device_info.pid)

        if device_info.get_ioter_name() is not None:
            device_type = device_info.get_ioter_name()
        elif "fed" in device_info.thread_type.casefold():
            device_type = "fed"
        elif "med" in device_info.thread_type.casefold():
            device_type = "med"
        elif "sed" in device_info.thread_type.casefold():
            device_type = "sed"
        else:
            device_type = "fed"

        path = Utils.get_script_path() + 'start'
        self.subProcess = Popen([path, run_param, device_type])
        self.set_pid(self.subProcess.pid)
        return self.pid

    ## Terminate chip all clusters process ##
    def terminate_chip_all_clusters(self, device_info, terminated=True):
        if self.pid != -1:
            self.terminate_process_tree()
        if terminated:
            Utils.remove_matter_files(device_info.device_num)
            Utils.remove_thread_setting_file(device_info.thread_setting_file)

    ## Terminate process tree ##
    def terminate_process_tree(self):
        print("terminateProcessTree : starting pid : " + str(self.pid))
        children = Process(self.pid).children(True)
        children.reverse()
        for child in children:
            print("get child pid : ", child.pid)
            try:
                if child.is_running():
                    print("try to terminate : ", child.pid)
                    child.send_signal(signal.SIGTERM)
                    child.wait(timeout=10)
            except TimeoutExpired as e:
                print(f"Timeout expired; exiting.", flush=True)
                child.kill()
            except Exception as e:
                print("exception : ", e)
        self.subProcess.terminate()
        self.subProcess.poll()
        self.set_pid(-1)
