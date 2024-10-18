"""
Configuration module for Growlithe.

This module defines the Config class, which manages the configuration settings
for the Growlithe application. It handles loading configurations from files,
setting default values, and managing derived paths.
"""

import yaml
import os
import platform
from growlithe.common.file_utils import create_dir_if_not_exists
from growlithe.common.logger import init_logger, logger
from typing import Dict, Any


class Config:
    """
    Singleton class for managing Growlithe configuration.

    This class handles loading, merging, and storing configuration settings
    for the Growlithe application. It ensures only one instance of the
    configuration is created and used throughout the application.
    """

    _instance = None

    def __new__(cls, config_path=None):
        """Ensure only one instance of Config is created."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path=None):
        """
        Initialize the Config instance.

        Args:
            config_path (str, optional): Path to the configuration file.
        """
        if self._initialized:
            return
        self._initialized = True

        self.config = {}

        default_config = self.get_defaults()

        if config_path and os.path.exists(config_path):
            print(f"Loading config from {config_path}")
            loaded_config = self.load_from_file(config_path)
            merged_config = self.merge_configs(default_config, loaded_config)
            if merged_config["cloud_provider"] == "GCP":
                merged_config["growlithe_lib_path"] = os.path.join(
                    os.path.dirname(__file__),
                    "enforcement",
                    "policy",
                    "template",
                    "growlithe_utils_gcp.py",
                )
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
        """
        Get the default configuration settings.
        Update the paths to attach debugger easily with Growlithe

        Returns:
            dict: Default configuration settings.
        """
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
                "enforcement",
                "policy",
                "template",
                "growlithe_utils_aws.py",
            ),
            "pydatalog_layer_path": os.path.join(
                os.path.dirname(__file__),
                "enforcement",
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
            "cloud_provider": "AWS",
        }

    def load_from_file(self, config_path):
        """
        Load configuration from a YAML file.

        Args:
            config_path (str): Path to the configuration file.

        Returns:
            dict: Loaded configuration.
        """
        with open(config_path, "r") as f:
            config_instance = yaml.safe_load(f)
        return config_instance

    def set_config_values(self, config_instance):
        """
        Set configuration values as attributes of the Config instance.

        Args:
            config_instance (dict): Configuration dictionary.
        """
        for key, val in config_instance.items():
            setattr(self, key, config_instance.get(key, val))

    def set_derived_paths(self):
        """Set derived paths based on the configuration values."""
        self.benchmark_path = os.path.dirname(self.app_config_path)
        self.app_path = self.benchmark_path
        self.src_path = os.path.join(self.app_path, self.src_dir)
        self.growlithe_path = os.path.join(os.path.dirname(self.app_path), f"growlithe_{self.app_name}")

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
        """Convert all path attributes to absolute paths."""
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
        """
        Generate a string representation of the configuration.

        Returns:
            str: Formatted string of configuration settings.
        """
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
        """
        Check if a key exists in the configuration.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return (
            key in self.__dict__.keys()
            and not key.startswith("_")
            and key not in ["config", "defaults"]
        )

    def merge_configs(
        self, default_config: Dict[str, Any], loaded_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge loaded configuration with default configuration.

        Args:
            default_config (Dict[str, Any]): Default configuration dictionary.
            loaded_config (Dict[str, Any]): Loaded configuration dictionary.

        Returns:
            Dict[str, Any]: Merged configuration dictionary.
        """
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


def get_config(config_path=None):
    """
    Get the Config instance.

    Args:
        config_path (str, optional): Path to the configuration file.

    Returns:
        Config: The Config instance.
    """
    return Config(config_path)
