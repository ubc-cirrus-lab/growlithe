"""
This is the main file for the project.
"""

import sys
from graph.adg.graph import Graph
from graph.codeql.analyzer import Analyzer
from graph.generater import GraphGenerator
from graph.parsers.sam import SAMParser
from graph.parsers.state_machine_parser import StepFunctionParser
from common.app_config import (
    app_config_path,
    app_config_type,
    app_name,
    app_path,
    growlithe_path,
    nodes_path,
    policy_spec_path,
)
from common.file_utils import create_dir_if_not_exists, detect_languages
from common.logger import logger
from common.tasks_config import CREATE_CODEQL_DB, PRODUCTION, RUN_CODEQL_QUERIES
from enforcer.taint.taint_tracker import TaintTracker


def main():
    languages: set[str] = detect_languages(path=app_path)

    # Run Static analysis
    create_dir_if_not_exists(path=growlithe_path)
    for language in languages:
        if CREATE_CODEQL_DB:
            Analyzer.create_ir(language=language)
        if RUN_CODEQL_QUERIES:
            Analyzer.run_queries(language=language)

    # Create a graph object
    graph: Graph = Graph(app_name)

    # Parse the SAM/cloud template of the application to get functions, resources and dependencies
    if app_config_type == "SAM":
        app_config_parser = SAMParser(app_config_path)
    elif app_config_type == "StepFunction":  # TODO: remove after sam for all benchmarks
        app_config_parser = StepFunctionParser("<Path to step func config>")
    else:
        logger.error("App config type not supported. Exiting...")
        sys.exit(1)

    graph.add_functions(app_config_parser.get_functions())
    graph.add_resources(app_config_parser.get_resources())

    # Update graph object with required nodes/edges
    graph_generator = GraphGenerator(graph)
    graph_generator.generate_intrafunction_graphs(app_config_parser.get_functions())
    graph_generator.add_metadata_edges(app_config_parser.get_functions())
    graph_generator.add_inter_function_edges(app_config_parser.get_resources())

    if not PRODUCTION:
        graph.dump_nodes_json(nodes_path)

    # Generate required policy template
    graph.dump_policy_edges_json(policy_spec_path)

    if not PRODUCTION:
        graph.visualize()

    # Enforcement

    if True:  # TODO: add check to add taint tracking only when needed
        taint_tracker = TaintTracker(graph=graph)
        # taint_tracker.run()
        # taint_tracker.save_files()


if __name__ == "__main__":
    main()
