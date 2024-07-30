import yaml
import os


class Config:
    def __init__(self, config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self.app_path = config.get("app_path", "")
        self.app_name = config.get("app_name", "")
        self.app_config_path = config.get("app_config_path", "")
        self.growlithe_path = config.get("growlithe_path", "")
        self.nodes_path = config.get("nodes_path", "")
        self.app_config_type = config.get("app_config_type", "")
        self.policy_spec_path = config.get("policy_spec_path", "")

        # Ensure all paths are absolute
        self.app_path = os.path.abspath(self.app_path)
        self.app_config_path = os.path.abspath(self.app_config_path)
        self.growlithe_path = os.path.abspath(self.growlithe_path)
        self.nodes_path = os.path.abspath(self.nodes_path)
        self.policy_spec_path = os.path.abspath(self.policy_spec_path)
