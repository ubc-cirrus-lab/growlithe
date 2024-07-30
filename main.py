"""
This is the main file for the project.
"""
from graph.parsers.sam import SAMParser
from graph.adg.graph import Graph
from graph.codeql.analyzer import Analyzer
from graph.generater import GraphGenerator
from common.app_config import app_path, app_name, app_config_path, growlithe_path, nodes_path, app_config_type, policy_spec_path
from common.tasks_config import CREATE_CODEQL_DB, GENERATE_EDGE_POLICY, RUN_CODEQL_QUERIES
from common.file_utils import create_dir_if_not_exists
from enforcer.taint.taint_tracker import TaintTracker
from common.file_utils import detect_languages
from common.logger import logger

from visualize import visualize

def main():
    languages: set[str] = detect_languages(path=app_path)
    logger.info(f"found languages in the source code: {languages}")

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
    if app_config_type == 'SAM':
        app_config_parser = SAMParser(app_config_path)
    else:
        logger.error(f"{app_config_type} is not supported. Only SAM templates are supported for now.")
        exit()
    if app_config_parser:
        graph.add_functions(app_config_parser.get_functions())
        graph.add_resources(app_config_parser.get_resources())

    # Update graph object with required nodes/edges
    graph_generator = GraphGenerator(graph)
    graph_generator.generate_intrafunction_graphs(app_config_parser.get_functions())
    graph_generator.add_metadata_edges(app_config_parser.get_functions())
    graph_generator.add_inter_function_edges(app_config_parser.get_resources())

    # graph.visualize()
    #visualize(graph)

    graph.dump_nodes_json(nodes_path)
    # Generate required policy templates
    if GENERATE_EDGE_POLICY:
        graph.dump_policy_edges_json(policy_spec_path)

    graph.get_updated_policy_json(policy_spec_path)

    # Enforcement 
    graph.enforce_policy()
    # Taint Tracking
    taint_tracker = TaintTracker(graph=graph)
    taint_tracker.run()
    taint_tracker.save_files()
    pass



if __name__ == "__main__":
    main()
