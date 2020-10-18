import json
import os


class Config:
    threshold = {}

    def __init__(self, config_path):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf8') as config_file:
                    self.threshold = json.load(config_file)
            else:
                self.threshold = {}
        except:
            self.threshold = {}

    def save_config(self):
        with open(self.config_path, 'w', encoding='utf8') as config_file:
            json.dump(self.threshold, config_file, ensure_ascii=False, indent=4)

    def set_threshold(self, gid, threshold):
        self.threshold[gid] = threshold
        self.save_config()

    def delete_threshold(self, gid):
        if gid in self.threshold:
            del self.threshold[gid]
            self.save_config()

