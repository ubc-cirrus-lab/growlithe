import yaml
import os
import platform
from growlithe.common.file_utils import create_dir_if_not_exists
from growlithe.common.logger import init_logger


class Config:
    _instance = None

    def __new__(cls, config_path=None):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path=None):
        if self._initialized:
            return
        self._initialized = True

        self.config = {}
        self.defaults = self.get_defaults()

        if config_path and os.path.exists(config_path):
            print(f"Loading config from {config_path}")
            self.load_from_file(config_path)
        elif config_path:
            print(f"Config file {config_path} not found. Using defaults.")
        else:
            print("No config file provided. Using defaults.")

        self.set_config_values()
        self.set_derived_paths()
        self.make_paths_absolute()

        create_dir_if_not_exists(self.growlithe_path)
        init_logger(self.profiler_log_path)

        print(self.__str__())

    def get_defaults(self):
        system_platform = platform.system()
        if system_platform == "Windows":
            growlithe_results_path = r"D:\Code\growlithe-results"
        elif system_platform == "Darwin":
            growlithe_results_path = "/Users/arshia/repos/ubc/final/growlithe-results"
        elif system_platform == "Linux":
            growlithe_results_path = "/app/tasks/"

        return {
            "growlithe_results_path": growlithe_results_path,
            "benchmark_name": "Benchmark2",
            "app_name": "ImageProcessing",
            "src_dir": "src",
            "app_config_type": "SAM",
            "app_config_path": os.path.join(
                growlithe_results_path, "Benchmark2", "ImageProcessing", "template.yaml"
            ),
        }

    def load_from_file(self, config_path):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def set_config_values(self):
        for key, default_value in self.defaults.items():
            setattr(self, key, self.config.get(key, default_value))

    def set_derived_paths(self):
        self.benchmark_path = os.path.dirname(self.app_config_path)
        self.app_path = self.benchmark_path
        self.src_path = os.path.join(self.app_path, self.src_dir)
        self.growlithe_path = os.path.join(os.path.dirname(self.app_path), "growlithe")

        self.new_app_path = os.path.join(
            self.growlithe_path, f"{self.app_name}_growlithe"
        )
        self.profiler_log_path = os.path.join(
            self.growlithe_path, "growlithe_profiler.log"
        )
        self.nodes_path = os.path.join(self.growlithe_path, "nodes.json")
        self.policy_spec_path = os.path.join(self.growlithe_path, "policy_spec.json")

    def make_paths_absolute(self):
        path_attributes = [
            "app_config_path",
            "benchmark_path",
            "app_path",
            "src_path",
            "new_app_path",
            "growlithe_path",
            "profiler_log_path",
            "nodes_path",
            "policy_spec_path",
        ]
        for attr in path_attributes:
            if hasattr(self, attr):
                setattr(self, attr, os.path.abspath(getattr(self, attr)))

    def __str__(self):
        return "\n".join(
            [
                f"{key}\t\t: {value}"
                for key, value in self.__dict__.items()
                if not key.startswith("_") and key != "config" and key != "defaults"
            ]
        )


# Usage
def get_config(config_path=None):
    return Config(config_path)
