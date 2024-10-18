"""
Main module for analyzing applications and generating dataflow graphs and policy templates.

This module provides functionality to analyze applications, generate Application Dependency Graphs (ADG),
and create policy templates based on the analysis results.
"""

import pickle
import click
import sys
from growlithe.graph.parsers.sam import SAMParser
from growlithe.graph.parsers.terraform import TerraformParser
from growlithe.graph.parsers.state_machine_parser import StepFunctionParser
from growlithe.graph.adg.graph import Graph
from growlithe.graph.codeql.intra_function_analyzer import Analyzer
from growlithe.graph.adg_generator import GraphGenerator
from growlithe.common.dev_config import (
    CREATE_CODEQL_DB,
    GENERATE_EDGE_POLICY,
    RUN_CODEQL_QUERIES,
)
from growlithe.common.file_utils import create_dir_if_not_exists, detect_languages
from growlithe.common.utils import profiler_decorator
from growlithe.config import get_config


@profiler_decorator
def analyze(config):
    """
    Analyze the application and generate dataflow graphs and policy templates.

    This function performs static analysis, parses application configuration,
    generates an Application Dependency Graph (ADG), and creates policy templates.

    Args:
        config: Configuration object containing analysis settings.

    Returns:
        Graph: The generated Application Dependency Graph.
    """
    sys.setrecursionlimit(3000)  # Increase the recursion limit to avoid RecursionError

    languages = detect_languages(path=config.app_path)

    # Run Static analysis
    create_dir_if_not_exists(path=config.growlithe_path)
    analyzer = Analyzer(config)
    for language in languages:
        if CREATE_CODEQL_DB:
            analyzer.create_codeql_database(language=language)
        if RUN_CODEQL_QUERIES:
            analyzer.run_codeql_queries(language=language)

    # Parse the SAM/cloud template of the application
    if config.app_config_type == "SAM":
        app_config_parser = SAMParser(config.app_config_path, config)
    elif config.app_config_type == "Terraform":
        app_config_parser = TerraformParser(config.app_config_path, config)
    elif config.app_config_type == "StepFunction":
        app_config_parser = StepFunctionParser(config.app_config_path)
    else:
        click.echo(
            f"Unsupported app_config_type: {config.app_config_type}", color="red"
        )
        return

    graph = generate_adg(app_config_parser, config)

    # Generate required policy templates
    if GENERATE_EDGE_POLICY:
        graph.dump_policy_edges_json(config.policy_spec_path)

    with open(config.graph_dump_path, "wb") as f:
        pickle.dump(graph, f)
    with open(config.config_dump_path, "wb") as f:
        pickle.dump(app_config_parser, f)

    click.echo("Analysis completed successfully!", color="green")
    return graph


@profiler_decorator
def generate_adg(app_config_parser, config):
    """
    Generate an Application Dependency Graph (ADG) based on the parsed application configuration.

    Args:
        app_config_parser: Parser object for the application configuration.
        config: Configuration object containing analysis settings.

    Returns:
        Graph: The generated Application Dependency Graph.
    """
    # Create a graph object
    graph = Graph(config.app_name)
    if app_config_parser:
        graph.add_functions(app_config_parser.get_functions())
        graph.add_resources(app_config_parser.get_resources())

    # Update graph object with required nodes/edges
    graph_generator = GraphGenerator(graph, config)
    graph_generator.generate_intrafunction_graphs(app_config_parser.get_functions())
    graph_generator.add_metadata_edges(app_config_parser.get_functions())
    graph_generator.add_inter_function_edges(app_config_parser.get_resources())

    graph.dump_nodes_json(config.nodes_path)

    return graph


if __name__ == "__main__":
    analyze(get_config(config_path=None))
