"""
Module for applying security policies and performing taint tracking on Application Dependency Graphs.

This module provides functionality to load previously analyzed graph data,
apply security policies, perform taint tracking, and update the application configuration.
"""

import pickle
import sys

from growlithe.graph.adg.graph import Graph
from growlithe.common.file_utils import save_files
from growlithe.enforcer.taint.taint_tracker import TaintTracker
from growlithe.config import Config, get_config
from growlithe.common.utils import profiler_decorator


@profiler_decorator
def apply(config: Config):
    """
    Apply security policies and perform taint tracking on the Application Dependency Graph.

    This function loads the previously analyzed graph data, applies security policies,
    performs taint tracking, and updates the application configuration.

    Args:
        config (Config): Configuration object containing application settings.
    """
    sys.setrecursionlimit(3000)  # Increase the recursion limit to avoid RecursionError
    graph, app_config_parser = load_dumps(config)
    graph.get_updated_policy_json(config.policy_spec_path)

    # Taint Tracking
    taint_tracker = TaintTracker(graph=graph, config=config)
    taint_tracker.run_taint_tracking()

    # Enforcement
    graph.enforce_policy()

    save_files(graph=graph, growlithe_lib_path=config.growlithe_lib_path)

    # Update the application configuration
    app_config_parser.modify_config(graph=graph)
    app_config_parser.save_config()


@profiler_decorator
def load_dumps(config: Config):
    """
    Load previously dumped graph and application configuration data.

    Args:
        config (Config): Configuration object containing file paths.

    Returns:
        tuple: A tuple containing the loaded Graph object and application configuration parser.
    """
    with open(config.graph_dump_path, "rb") as f:
        graph: Graph = pickle.load(f)

    # Minor FIXME: config values use the config which was used when analyze was run,
    # Updates to config before running apply is not taken
    with open(config.config_dump_path, "rb") as f:
        app_config_parser = pickle.load(f)

    return graph, app_config_parser


if __name__ == "__main__":
    apply(get_config(config_path=None))
