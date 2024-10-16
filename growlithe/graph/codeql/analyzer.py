import subprocess
import pathlib
import re
import os

from growlithe.common.logger import logger
from growlithe.common.tasks_config import codeql_queries
from growlithe.common.file_utils import get_language_files
from growlithe.common.utils import profiler_decorator
from growlithe.config import Config


class Analyzer:
    def __init__(self, config: Config):
        self.config = config

    """Generate CodeQL intermediate representation (IR) or the database for an app for a specific language."""

    @profiler_decorator
    def create_codeql_database(self, language):
        logger.info(f"Creating CodeQL database in {self.config.growlithe_path}")
        try:
            logger.info(f'Running codeql database create {self.config.app_name}_codeql_ir_{language} --language={language} --overwrite -j=0 -M=2048 -s={self.config.app_path}')
            subprocess.run(
                f"(cd {self.config.growlithe_path}\
                    && codeql database create {self.config.app_name}_codeql_ir_{language}\
                    --language={language}\
                    --overwrite\
                    -j=0\
                    -M=2048\
                    -s={self.config.app_path})",
                shell=True,
                stdout=subprocess.DEVNULL,
            )
        except Exception as e:
            logger.error(f"Error while creating CodeQL database: {e}")
            raise Exception(f"Error while creating CodeQL database: {e}")
        logger.info(
            f"CodeQL database created: {self.config.app_name}_codeql_ir_{language}"
        )

    """Run CodeQL queries on the CodeQL intermediate representation (IR) or the database for an app for a specific language."""

    @profiler_decorator
    def run_codeql_queries(self, language):
        current_dir: str = pathlib.Path(__file__).parent.resolve()
        functions: list[str] = get_language_files(
            root=self.config.app_path, language=language, src_dir=self.config.src_dir, growlithe_path=self.config.growlithe_path
        )
        logger.info(
            f"Running CodeQL queries for {language} in {self.config.app_name}: {', '.join(codeql_queries)}"
        )
        logger.info(f"Analyzing functions for: {', '.join(functions)}")
        update_query_config(current_dir, language, functions)

        for query_file in codeql_queries:
            query_output_path: str = os.path.join(
                self.config.growlithe_path, f"{query_file}_{language}.sarif"
            )
            try:
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
                            f"{self.config.app_name}_codeql_ir_{language}",
                        ),
                        os.path.join(
                            current_dir, language, "queries", f"{query_file}.ql"
                        ),
                        "--warnings",
                        "hide",
                    ],
                    stdout=subprocess.DEVNULL,
                    # stderr=subprocess.DEVNULL,
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
    codeql_config_path: str = os.path.join(current_dir, language, "queries", "Config.qll")
    with open(codeql_config_path, "r") as file:
        config_template: str = file.read()

    # Convert the Python list to a string
    array_string: str = ",\n\t\t".join([f'"{item}"' for item in functions])
    # Create the final string in the desired format

    result_string: str = f"result = [{array_string}]"
    pattern: re.Pattern = re.compile(r"result\s*=\s*\[.*?\]", re.DOTALL)
    if not re.search(pattern, config_template):
        logger.error("Could not find result variable in Config.qll")
        raise Exception("Could not find result variable in Config.qll")

    content: str = pattern.sub(result_string, config_template)
    with open(codeql_config_path, "w") as file:
        file.write(content)
    logger.info(f"Updated {codeql_config_path} to analyze required functions.")


# import subprocess
# import pathlib
# import re
# import os

# from growlithe.common.logger import logger
# from growlithe.common.app_config import *
# from growlithe.common.tasks_config import codeql_queries
# from growlithe.common.file_utils import get_language_files
# from growlithe.common.utils import profiler_decorator
# from growlithe.config import Config

# class Analyzer:
#     def __init__(self, config: Config):
#         self.config = config

#     """Generate CodeQL intermediate representation (IR) or the database for an app for a specific language."""

#     @profiler_decorator
#     def create_ir(self, language):

#         logger.info(f"Creating CodeQL database in {self.config.growlithe_path}")
#         try:
#             subprocess.run(
#                 f"(cd {self.config.growlithe_path}\
#                     && codeql database create {self.config.app_name}_codeql_ir_{language}\
#                     --language={language}\
#                     --overwrite\
#                     -j=0\
#                     -M=2048\
#                     -s={self.config.app_path})",
#                 shell=True,
#                 stdout=subprocess.DEVNULL,
#             )
#         except Exception as e:
#             logger.error(f"Error while creating CodeQL database: {e}")
#             raise Exception(f"Error while creating CodeQL database: {e}")
#         logger.info(f"CodeQL database created: {self.config.app_name}_codeql_ir_{language}")

#     """Run CodeQL queries on the CodeQL intermediate representation (IR) or the database for an app for a specific language."""
#     @profiler_decorator
#     def run_queries(self, language):
#         current_dir: str = pathlib.Path(__file__).parent.resolve()
#         functions: list[str] = get_language_files(
#             root=self.config.app_path, language=language
#         )
#         logger.info(
#             f"Running CodeQL queries for {language} in {self.config.app_name}: {', '.join(codeql_queries)}"
#         )
#         logger.info(f"Analyzing functions for: {', '.join(functions)}")
#         update_query_config(current_dir, language, functions)

#         for query_file in codeql_queries:
#             query_output_path: str = os.path.join(
#                 self.config.growlithe_path, f"{query_file}_{language}.sarif"
#             )
#             try:
#                 subprocess.run(
#                     [
#                         "codeql",
#                         "database",
#                         "analyze",
#                         "-q",
#                         "--output",
#                         query_output_path,
#                         "--format",
#                         "sarifv2.1.0",
#                         "--rerun",
#                         "-M",
#                         "2048",
#                         "--threads",
#                         "0",
#                         "--max-disk-cache",
#                         "0",
#                         os.path.join(
#                             self.config.growlithe_path,
#                             f"{self.config.app_name}_codeql_ir_{language}",
#                         ),
#                         os.path.join(
#                             current_dir, language, "queries", f"{query_file}.ql"
#                         ),
#                         "--warnings",
#                         "hide",
#                     ],
#                     stdout=subprocess.DEVNULL,
#                     # stderr=subprocess.DEVNULL,
#                 )
#             except Exception as e:
#                 logger.error(f"Error while running CodeQL queries: {e}")
#                 raise Exception(f"Error while running CodeQL queries: {e}")
#             logger.info(
#                 f"Saved CodeQL query output for {query_file} to {query_output_path}"
#             )
#         logger.info(
#             f"CodeQL queries run successfully for {language} in {self.config.app_name}"
#         )


# def update_query_config(current_dir, language, functions):
#     codeql_config_path: str = f"{current_dir}/{language}/queries/Config.qll"
#     with open(codeql_config_path, "r") as file:
#         config_template: str = file.read()

#     # Convert the Python list to a string
#     array_string: str = ",\n\t\t".join([f'"{item}"' for item in functions])
#     # Create the final string in the desired format

#     result_string: str = f"result = [{array_string}]"
#     pattern: re.Pattern = re.compile(r"result\s*=\s*\[.*?\]", re.DOTALL)
#     if not re.search(pattern, config_template):
#         logger.error("Could not find result variable in Config.qll")
#         raise Exception("Could not find result variable in Config.qll")

#     content: str = pattern.sub(result_string, config_template)
#     with open(codeql_config_path, "w") as file:
#         file.write(content)
#     logger.info(f"Updated {codeql_config_path} to analyze required functions.")
