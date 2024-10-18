"""
Module for analyzing intra-function dataflows using CodeQL.

This module provides functionality to create CodeQL databases and run CodeQL queries
on application code.
"""

import subprocess
import pathlib
import re
import os

from growlithe.common.logger import logger
from growlithe.common.dev_config import codeql_queries
from growlithe.common.file_utils import get_language_files
from growlithe.common.utils import profiler_decorator
from growlithe.config import Config


class Analyzer:
    """
    A class for performing CodeQL analysis on application code.

    This class provides methods to create CodeQL databases and run CodeQL queries
    for specific programming languages.
    """

    def __init__(self, config: Config):
        """
        Initialize the Analyzer with a configuration object.

        Args:
            config (Config): Configuration object containing analysis settings.
        """
        self.config = config

    @profiler_decorator
    def create_codeql_database(self, language):
        """
        Generate CodeQL intermediate representation (IR) or database for an app in a specific language.

        Args:
            language (str): The programming language of the application.

        Raises:
            Exception: If there's an error during database creation.
        """
        logger.info(f"Creating CodeQL database in {self.config.growlithe_path}")
        try:
            # CodeQL database creation command
            subprocess.run(
                f"(cd {self.config.growlithe_path} && codeql database create codeql_ir_{language} --language={language} --overwrite -j=0 -M=2048 -s={self.config.app_path})",
                shell=True,
                stdout=subprocess.DEVNULL,
            )
        except Exception as e:
            logger.error(f"Error while creating CodeQL database: {e}")
            raise Exception(f"Error while creating CodeQL database: {e}")
        logger.info(
            f"CodeQL database created: codeql_ir_{language}"
        )

    @profiler_decorator
    def run_codeql_queries(self, language):
        """
        Run CodeQL queries on the CodeQL database for an app in a specific language.

        Args:
            language (str): The programming language of the application.

        Raises:
            Exception: If there's an error during query execution.
        """
        current_dir = pathlib.Path(__file__).parent.resolve()
        functions = get_language_files(
            root=self.config.app_path,
            language=language,
            src_dir=self.config.src_dir,
            growlithe_path=self.config.growlithe_path,
        )
        logger.info(
            f"Running CodeQL queries for {language} in {self.config.app_name}: {', '.join(codeql_queries)}"
        )
        logger.info(f"Analyzing functions for: {', '.join(functions)}")
        update_query_config(current_dir, language, functions)

        for query_file in codeql_queries:
            query_output_path = os.path.join(
                self.config.growlithe_path, f"{query_file}_{language}.sarif"
            )
            try:
                # CodeQL query execution command
                subprocess.run(
                    [
                        "codeql",
                        "database",
                        "analyze",
                        "-q",
                        "--output",
                        query_output_path,
                        "--format",
                        "sarifv2.1.0",
                        "--rerun",
                        "-M",
                        "2048",
                        "--threads",
                        "0",
                        "--max-disk-cache",
                        "0",
                        os.path.join(
                            self.config.growlithe_path,
                            f"codeql_ir_{language}",
                        ),
                        os.path.join(
                            current_dir, language, "queries", f"{query_file}.ql"
                        ),
                        "--warnings",
                        "hide",
                    ],
                    stdout=subprocess.DEVNULL,
                )
            except Exception as e:
                logger.error(f"Error while running CodeQL queries: {e}")
                raise Exception(f"Error while running CodeQL queries: {e}")
            logger.info(
                f"Saved CodeQL query output for {query_file} to {query_output_path}"
            )
        logger.info(
            f"CodeQL queries run successfully for {language} in {self.config.app_name}"
        )


def update_query_config(current_dir, language, functions):
    """
    Update the CodeQL query configuration file with the list of functions to analyze.

    Args:
        current_dir (str): The current directory path.
        language (str): The programming language of the application.
        functions (list): List of functions to be analyzed.

    Raises:
        Exception: If the result variable is not found in the Config.qll file.
    """
    codeql_config_path = os.path.join(current_dir, language, "queries", "Config.qll")
    with open(codeql_config_path, "r") as file:
        config_template = file.read()

    array_string = ",\n\t\t".join([f'"{item}"' for item in functions])
    result_string = f"result = [{array_string}]"
    pattern = re.compile(r"result\s*=\s*\[.*?\]", re.DOTALL)
    if not re.search(pattern, config_template):
        logger.error("Could not find result variable in Config.qll")
        raise Exception("Could not find result variable in Config.qll")

    content = pattern.sub(result_string, config_template)
    with open(codeql_config_path, "w") as file:
        file.write(content)
    logger.info(f"Updated {codeql_config_path} to analyze required functions.")
