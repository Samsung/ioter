from common.utils import Utils
import json

class Config:
    def __init__(cls):
        super(Config, cls).__init__()
        cls.load()

    def init_config_data(cls):
        cls.option_menu_shown = False
        cls.thread_debug_level = 4
        cls.default_thread_type = 'fed'
        cls.auto_onboarding_debug_mode = False

    def load(cls):
        try:
            with open(Utils.get_config_path(), 'r') as f:
                config_data = json.load(f)
            cls.option_menu_shown = config_data['option_menu_shown']
            cls.thread_debug_level = config_data['thread_debug_level']
            cls.default_thread_type = config_data['default_thread_type']
            cls.auto_onboarding_debug_mode = config_data['auto_onboarding_debug_mode']
        except Exception:
            cls.init_config_data()

    def save(cls):
        config_data = {
            'option_menu_shown': cls.option_menu_shown,
            'thread_debug_level': cls.thread_debug_level,
            'default_thread_type': cls.default_thread_type,
            'auto_onboarding_debug_mode': cls.auto_onboarding_debug_mode
        }
        try:
            with open(Utils.get_config_path(), 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception:
            print("failed to save config data")
