import json

class ConfigLoader(): 
    def __init__(self, config_FilePath):
        self.cfg = json.load(open(config_FilePath))
        self.app_cfg = self.cfg["app"]
    @property
    def context_file_path(self): 
        return self.app_cfg["context_file_path"]
    @property
    def input_links(self): 
        with open(self.app_cfg["input_links_file"], "r") as f: 
            links = [l.strip() for l in f if l.strip()]
        return links
    @property
    def drive_folder_id(self):
        return self.app_cfg["drive_folder_id"]
    @property
    def github_token(self): 
        return self.app_cfg["github_token"]
    @property 
    def HUGGINGFACE_HUB_TOKEN(self): 
        return self.app_cfg["HUGGINGFACE_HUB_TOKEN"]
    @property
    def repo_path(self):
        return self.app_cfg["repo_path"]
    @property 
    def repo_owner(self): 
        return self.app_cfg["repo_owner"]