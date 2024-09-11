import pickle

from growlithe.graph.adg.graph import Graph
from growlithe.common.file_utils import save_files
from growlithe.enforcer.taint.taint_tracker import TaintTracker
from growlithe.config import Config
from growlithe.common.utils import profiler_decorator

@profiler_decorator
def apply(config: Config):
    with open(config.graph_dump_path, "rb") as f:
        graph: Graph = pickle.load(f)
    print("0", config.pydatalog_layer_path)
    with open(config.config_dump_path, "rb") as f:
        app_config_parser = pickle.load(f)
    print("1", config.pydatalog_layer_path)

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
