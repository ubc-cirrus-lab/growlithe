import subprocess
import os, re
import pathlib

from src.utility import create_dir_if_not_exists
from src.logger import logger, profiler_logger
import time, shutil


class CodeQL:
    @staticmethod
    def analyze(app_path, queries, rerun_db_create, rerun_queries, language, num_runs=1):
        
        db_create_time_list = []
        query_time_list = []
        for i in range(num_runs):
            profiler_logger.info(f"Running iteration {i+1}/{num_runs} of CodeQL analysis...")

            app_path = f"{pathlib.Path(app_path).resolve()}"
            growlithe_path = f"{app_path}/../growlithe/"
            create_dir_if_not_exists(growlithe_path)
            codeql_db_name = f"codeqldb_{language}/"
            codeql_db_path = f"{growlithe_path}/{codeql_db_name}/"
            output_path = f"{growlithe_path}/output/"

            if rerun_db_create or not os.path.exists(codeql_db_path):
                if os.path.exists(codeql_db_path):
                    logger.info("Deleting existing database...")
                    shutil.rmtree(codeql_db_path, ignore_errors=False, onerror=None)
                    logger.info("Existing database deleted")

                start_time = time.time()
                CodeQL._create_database(app_path, growlithe_path, language, codeql_db_name)
                printPattern("*", 75)
                db_create_time_list.append(time.time() - start_time)
                profiler_logger.info(
                    f"CodeQL database created in {time.time() - start_time} seconds"
                )
                printPattern("*", 75)
            else:
                logger.info(
                    f"Expecting CodeQL database at {codeql_db_path} - skipping database creation"
                )

            if rerun_queries:
                start_time = time.time()
                CodeQL._analyze_functions(app_path, codeql_db_path, language, output_path, queries)
                query_time_list.append(time.time() - start_time)
            else:
                logger.info(
                    f"CodeQL analysis output already exists at {output_path} - skipping analysis"
                )
                
            logger.info(f"Iteration {i+1}/{num_runs} of CodeQL analysis complete")
        if len(db_create_time_list) > 0:
            logger.info(
                f"profiler_logger database creation time over {num_runs} iterations: {sum(db_create_time_list)/len(db_create_time_list)} seconds"
            )
        if len(query_time_list) > 0:
            profiler_logger.info(
                f"Average query time over {num_runs} iterations: {sum(query_time_list)/len(query_time_list)} seconds"
            )

    @staticmethod
    def _analyze_functions(app_path, codeql_db_path, language, output_path, queries):
        current_dir = pathlib.Path(__file__).parent.resolve()

        functions = find_python_files(app_path)
        logger.info(f"Found {len(functions)} functions to analyze: ")
        logger.info(functions)

        codeql_config_path = f"{current_dir}/{language}/queries/Config.qll"
        with open(codeql_config_path, "r") as file:
            config_template = file.read()

        # Convert the Python list to a string
        array_string = ",\n\t\t".join([f'"{item}"' for item in functions])
        # Create the final string in the desired format
        result_string = f"result = [{array_string}]"
        pattern = re.compile(r"result\s*=\s*\[.*?\]", re.DOTALL)
        if not re.search(pattern, config_template):
            raise Exception("Could not find result variable in Config.qll")

        content = pattern.sub(result_string, config_template)

        with open(codeql_config_path, "w") as file:
            file.write(content)

        logger.info(f"Rewritten {codeql_config_path} to add {result_string} ")

        for query_file in queries:
            printPattern("-", 75)
            logger.info(f"Running query {query_file}")
            printPattern("-", 75)
            start_time = time.time()
            subprocess.run(
                [
                    "codeql",
                    "database",
                    "analyze",
                    "-q",
                    "--output",
                    f"{output_path}/{query_file}_{language}.sarif",
                    "--format",
                    "sarifv2.1.0",
                    "--rerun",
                    "-M",
                    "2048",
                    "--threads",
                    "0",
                    "--max-disk-cache",
                    "0",
                    codeql_db_path,
                    f"{current_dir}/{language}/queries/{query_file}.ql",
                ],
                stdout=subprocess.DEVNULL,
            )

            printPattern("*", 75)
            profiler_logger.info(
                f"Query {query_file} with {len(functions)} functions took {time.time() - start_time} seconds"
            )
            printPattern("*", 75)

    @staticmethod
    def _create_database(app_path, growlithe_path, language, codeql_db_name):
        printPattern("*", 75)
        logger.info(f"Creating CodeQL database in {growlithe_path}")
        subprocess.run(
            f"(cd {growlithe_path} && codeql database create {codeql_db_name} --language={language} --overwrite -j=0 -M=2048 -s={app_path})",
            shell=True,
            stdout=subprocess.DEVNULL,
        )
        logger.info("CodeQL database created")


def printPattern(pattern, length):
    logger.info(pattern * length)


def find_python_files(folder_path):
    python_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                relative_path = os.path.relpath(os.path.join(root, file), folder_path)
                relative_path = relative_path.replace(os.path.sep, "/")

                python_files.append(relative_path)

    return python_files


def function_path_to_name(function_path):
    return function_path.replace("/", "_").replace(".", "_")
