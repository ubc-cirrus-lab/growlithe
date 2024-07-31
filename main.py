"""
This is the main file for the project.
"""

from growlithe.graph.parsers.sam import SAMParser
from growlithe.graph.adg.graph import Graph
from growlithe.graph.codeql.analyzer import Analyzer
from growlithe.graph.generater import GraphGenerator

from growlithe.common.tasks_config import (
    CREATE_CODEQL_DB,
    GENERATE_EDGE_POLICY,
    RUN_CODEQL_QUERIES,
)
from growlithe.common.file_utils import create_dir_if_not_exists
from growlithe.enforcer.taint.taint_tracker import TaintTracker
from growlithe.graph.parsers.state_machine_parser import StepFunctionParser
from growlithe.common.file_utils import detect_languages
from growlithe.config import get_config

# from visualize import visualize


def main():

    config = get_config()
    languages: set[str] = detect_languages(path=config.app_path)

    # Run Static analysis
    create_dir_if_not_exists(path=config.growlithe_path)
        analyzer = Analyzer(config)
    for language in languages:
        if CREATE_CODEQL_DB:
            analyzer.create_ir(language=language)
        if RUN_CODEQL_QUERIES:
            analyzer.run_queries(language=language)

    # Create a graph object
    graph: Graph = Graph(config.app_name)

    # Parse the SAM/cloud template of the application to get functions, resources and dependencies
    if config.app_config_type == "SAM":
        app_config_parser = SAMParser(config.app_config_path)
    elif config.app_config_type == "StepFunction":
        app_config_parser = StepFunctionParser("<Path to step func config>")
    if app_config_parser:
        graph.add_functions(app_config_parser.get_functions())
        graph.add_resources(app_config_parser.get_resources())

    # Update graph object with required nodes/edges
    graph_generator = GraphGenerator(graph)
    graph_generator.generate_intrafunction_graphs(app_config_parser.get_functions())
    graph_generator.add_metadata_edges(app_config_parser.get_functions())
    graph_generator.add_inter_function_edges(app_config_parser.get_resources())

    # visualize(graph)

    graph.dump_nodes_json(config.nodes_path)
    # Generate required policy templates
    if GENERATE_EDGE_POLICY:
        graph.dump_policy_edges_json(config.policy_spec_path)

    graph.get_updated_policy_json(config.policy_spec_path)
    # Enforcement
    graph.enforce_policy()
    # Taint Tracking
    taint_tracker = TaintTracker(graph=graph)
    taint_tracker.run()
    taint_tracker.save_files()
    pass


if __name__ == "__main__":
    main()
