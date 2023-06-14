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
# File : config.py
# Description: Initialize, save and load ioter main window configutation

from common.utils import Utils
import json

## Main Config Class ##
class Config:
    def __init__(cls):
        super(Config, cls).__init__()
        cls.load()

    ## Initialize default config ##
    def init_config_data(cls):
        cls.option_menu_shown = False
        cls.thread_debug_level = 4
        cls.default_thread_type = 'fed'
        cls.auto_onboarding_debug_mode = False
        cls.version = ""

    ## Load config ##
    def load(cls):
        try:
            with open(Utils.get_config_path(), 'r') as f:
                config_data = json.load(f)
            cls.option_menu_shown = config_data['option_menu_shown']
            cls.thread_debug_level = config_data['thread_debug_level']
            cls.default_thread_type = config_data['default_thread_type']
            cls.auto_onboarding_debug_mode = config_data['auto_onboarding_debug_mode']
            cls.version = config_data['version']
        except Exception:
            cls.init_config_data()
    ## Save config ##
    def save(cls):
        config_data = {
            'option_menu_shown': cls.option_menu_shown,
            'thread_debug_level': cls.thread_debug_level,
            'default_thread_type': cls.default_thread_type,
            'auto_onboarding_debug_mode': cls.auto_onboarding_debug_mode,
            'version': cls.version        }
        try:
            with open(Utils.get_config_path(), 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception:
            print("failed to save config data")
