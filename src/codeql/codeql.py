import subprocess
import os
import pathlib
import glob

from src.logger import logger


class CodeQL:
    @staticmethod
    def analyze(app_path):
        logger.info("Running CodeQL analysis...")

        app_path = f'{pathlib.Path(app_path).resolve()}'
        codeql_db_path = f'{app_path}/codeqldb/'
        output_dir = f'{app_path}/output/'

        if os.path.exists(codeql_db_path):
            logger.info(f'CodeQL database already exists at {codeql_db_path} - skipping database creation')
        else:
            CodeQL._create_database(app_path)

        if os.path.exists(output_dir):
            logger.info(f'CodeQL analysis output already exists at {output_dir} - skipping analysis')
        else:
            CodeQL._analyze_functions(app_path, codeql_db_path, output_dir)

        logger.info('CodeQL analysis complete')

    @staticmethod
    def _analyze_functions(app_path, codeql_db_path, output_dir):
        current_dir = pathlib.Path(__file__).parent.resolve()
        # queries = ['getSources', 'getSinks', 'flowPaths', 'sinkConditions']
        # queries = ['getSources', 'getSinks', 'flowPaths']
        queries = ['flowPaths']

        if(os.path.exists(output_dir)):
            logger.info('Deleting existing output files...')
            for file in glob.glob(f'{output_dir}/*'):
                os.remove(file)
            logger.info('Existing output directory deleted')
        else:
            logger.info('Creating output directory...')
            os.mkdir(output_dir)
            logger.info('Output directory created')

        functions = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(f'{app_path}/*.py')]

        logger.info(f"Found {len(functions)} functions to analyze: ")
        logger.info(functions)

        codeql_config_path = f'{current_dir}/queries/Config.qll'
        with open(codeql_config_path, 'r') as file:
            config_template = file.read()
        to_replace = 'test.py'

        for function in functions:
            logger.info(f'Analyzing function {function}')
            config = config_template.replace(to_replace, f"{function}.py")
            with open(codeql_config_path, 'w') as file:
                file.write(config)
            for query_file in queries:
                subprocess.run(
                    ['codeql', 'database', 'analyze', '--output', f'{output_dir}/{function}_{query_file}.sarif',
                     '--format', 'sarifv2.1.0', '--rerun', codeql_db_path,
                     f'{current_dir}/queries/{query_file}.ql'], stdout=subprocess.DEVNULL)

    @staticmethod
    def _create_database(app_path):
        logger.info('Creating CodeQL database...')
        subprocess.run(
            f'(cd {app_path} && codeql database create codeqldb --language=python --overwrite)',
            shell=True, stdout=subprocess.DEVNULL)
        logger.info('CodeQL database created')
