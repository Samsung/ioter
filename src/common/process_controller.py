from common.utils import Utils

import signal
from psutil import *
from subprocess import *

global run_param_chip_all_clusters_format
run_param_chip_all_clusters_format = \
    "--device-id %s --discriminator %s --thread "\
    "--thread-version %s --com-port %s "\
    "--thread-debug %s --device-num %s " \
    "--vendor-id %s --product-id %s "


class ProcessController():
    def __init__(self):
        self.pid = -1

    def get_pid(self):
        # print("current pid : " + str(self.pid))
        return self.pid

    def set_pid(self, pid):
        print("PID change from " + str(self.pid) + " to " + str(pid))
        self.pid = pid

    def launch_chip_all_clusters(self, device_info):
        run_param = run_param_chip_all_clusters_format % (device_info.device_id, device_info.discriminator,
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

    def terminate_chip_all_clusters(self, device_info, terminated=True):
        if self.pid != -1:
            self.terminate_process_tree()
        if (terminated):
            Utils.remove_matter_files(device_info.device_num)
            Utils.remove_thread_setting_file(device_info.thread_setting_file)

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
