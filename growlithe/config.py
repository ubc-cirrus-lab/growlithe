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

        # Set default values based on platform
        self.set_platform_defaults()

        # Set default values for the selected benchmark
        self.set_benchmark_defaults()

        # Override defaults with values from config file if provided
        if config_path:
            print(f"Loading config from {config_path}")
            self.load_from_file(config_path)
        else:
            print("No config file provided. Using defaults.")

        # Ensure all paths are absolute
        self.make_paths_absolute()

        create_dir_if_not_exists(self.growlithe_path)
        init_logger(self.profiler_log_path)

    def set_platform_defaults(self):
        system_platform = platform.system()
        if system_platform == "Windows":
            self.growlithe_results_path = r"D:\Code\growlithe-results"
        elif system_platform == "Darwin":
            self.growlithe_results_path = (
                "/Users/arshia/repos/ubc/final/growlithe-results"
            )
        elif system_platform == "Linux":
            self.growlithe_results_path = "/app/tasks/"

    def set_benchmark_defaults(self):
        # Uncomment the benchmark you want to use as default

        # ########## Benchmark1 #############
        # self.benchmark_name = "Benchmark1"
        # self.app_name = "ClaimProcessing"
        # self.src_dir = "src"
        # self.app_config_type = "SAM"
        # self.app_config_path = ""
        # ########## Benchmark1 #############

        ########## Benchmark2 #############
        self.benchmark_name = "Benchmark2"
        self.app_name = "ImageProcessing"
        self.src_dir = "src"
        self.app_config_type = "SAM"
        self.app_config_path = os.path.join(
            self.growlithe_results_path,
            self.benchmark_name,
            self.app_name,
            "template.yaml",
        )
        ########## Benchmark2 #############

        # ########## Benchmark3 #############
        # self.benchmark_name = "Benchmark3"
        # self.app_name = "ShoppingCart"
        # self.src_dir = "src"
        # self.app_config_type = "StepFunction"
        # self.app_config_path = ""
        # ########## Benchmark3 #############

        # Set derived paths
        self.benchmark_path = os.path.join(
            self.growlithe_results_path, self.benchmark_name
        )
        self.app_path = os.path.join(self.benchmark_path, self.app_name)
        self.src_path = os.path.join(self.app_path, self.src_dir)
        self.new_app_path = os.path.join(
            self.benchmark_path, f"{self.app_name}Growlithe"
        )
        self.growlithe_path = os.path.join(self.benchmark_path, "Growlithe")
        self.profiler_log_path = os.path.join(
            self.growlithe_path, "growlithe_profiler.log"
        )
        self.nodes_path = os.path.join(self.growlithe_path, "nodes.json")
        self.policy_spec_path = os.path.join(self.growlithe_path, "policy_spec.json")

    def load_from_file(self, config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Override default values with those from the config file
        for key, value in config.items():
            setattr(self, key, value)

    def make_paths_absolute(self):
        path_attributes = [
            "growlithe_results_path",
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


# Usage
def get_config(config_path=None):
    return Config(config_path)
