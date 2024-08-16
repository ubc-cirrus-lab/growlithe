import pickle

import growlithe.graph.adg.graph
from growlithe.common.file_utils import save_files
from growlithe.enforcer.taint.taint_tracker import TaintTracker


def apply(config):
    with open(config.graph_dump_path, "rb") as f:
        graph = pickle.load(f)
    with open(config.config_dump_path, "rb") as f:
        app_config_parser = pickle.load(f)

    graph.get_updated_policy_json(config.policy_spec_path)
    # Enforcement
    graph.enforce_policy()
    # Taint Tracking
    taint_tracker = TaintTracker(graph=graph, config=config)
    taint_tracker.run()
    save_files(graph=graph, growlithe_lib_path=config.growlithe_lib_path)

    # Update the application configuration
    app_config_parser.modify_config(graph=graph)
    app_config_parser.save_config()
