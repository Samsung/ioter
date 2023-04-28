from common.utils import Utils

import json

class Config:
    CONFIG_FILE = Utils.get_tmp_path() + 'config.json'
    test_window_shown = False

    @classmethod
    def load(cls):
        try:
            with open(cls.CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
            cls.test_window_shown = config_data.get('test_window_shown', cls.test_window_shown)
        except Exception:
            pass

    @classmethod
    def save(cls):
        config_data = {'test_window_shown': cls.test_window_shown}
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(config_data, f)