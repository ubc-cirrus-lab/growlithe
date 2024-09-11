import yaml
import os
import platform
from growlithe.common.file_utils import create_dir_if_not_exists
from growlithe.common.logger import init_logger, logger
from typing import Dict, Any

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

        default_config = self.get_defaults()

        if config_path and os.path.exists(config_path):
            print(f"Loading config from {config_path}")
            loaded_config = self.load_from_file(config_path)
            merged_config = self.merge_configs(default_config, loaded_config)
        else:
            print("No config file provided, or it doesn't exist. Using defaults.")
            merged_config = default_config

        self.set_config_values(merged_config)
        self.set_derived_paths()
        self.make_paths_absolute()

        create_dir_if_not_exists(self.growlithe_path)
        init_logger(self.profiler_log_path)

        logger.info(self.__str__())

    def get_defaults(self):
        system_platform = platform.system()
        if system_platform == "Windows":
            growlithe_results_path = r"D:\Code\growlithe-results"
        elif system_platform == "Darwin":
            growlithe_results_path = "/Users/arshia/repos/ubc/growlithe-results"
        elif system_platform == "Linux":
            growlithe_results_path = "/app/tasks/"

        return {
            "growlithe_results_path": growlithe_results_path,
            "growlithe_lib_path": os.path.join(
                os.path.dirname(__file__),
                "enforcer",
                "policy",
                "template",
                "growlithe.py",
            ),
            "pydatalog_layer_path": os.path.join(
                os.path.dirname(__file__),
                "enforcer",
                "policy",
                "template",
                "pydatalog.zip",
            ),
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
            config_instance = yaml.safe_load(f)
        return config_instance

    def set_config_values(self, config_instance):
        for key, val in config_instance.items():
            setattr(self, key, config_instance.get(key, val))

    def set_derived_paths(self):
        self.benchmark_path = os.path.dirname(self.app_config_path)
        self.app_path = self.benchmark_path
        self.src_path = os.path.join(self.app_path, self.src_dir)
        self.growlithe_path = os.path.join(os.path.dirname(self.app_path), "growlithe")

        self.graph_dump_path = os.path.join(self.growlithe_path, "graph_dump.pkl")
        self.config_dump_path = os.path.join(self.growlithe_path, "config_dump.pkl")
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
            "graph_dump_path",
            "config_dump_path",
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
        header = "Growlithe is using the following configuration:"
        separator = "=" * 72

        config_items = [
            f"{key:<20} : {value}"
            for key, value in self.__dict__.items()
            if not key.startswith("_") and key not in ["config", "defaults"]
        ]

        return (
            f"{separator}\n{header}\n{separator}\n"
            + "\n".join(config_items)
            + f"\n{separator}"
        )

    def has_key(self, key):
        return (
            key in self.__dict__.keys()
            and not key.startswith("_")
            and key not in ["config", "defaults"]
        )
    def merge_configs(self, default_config: Dict[str, Any], loaded_config: Dict[str, Any]) -> Dict[str, Any]:
        merged = default_config.copy()
        for key, value in loaded_config.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self.merge_configs(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value
        return merged


# Usage
def get_config(config_path=None):
    return Config(config_path)
