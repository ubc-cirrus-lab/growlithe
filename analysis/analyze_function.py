import os
import subprocess

root_path = '../'
benchmark_path = f'{root_path}/benchmarks/ImageProcessingStateMachine/'
functions_path = f'{benchmark_path}/LambdaFunctions/'
codeql_db_path = f'{benchmark_path}/codeqldb/'
codeql_src_path = f'{root_path}/src/'

queries = ['getSources', 'getSinks', 'flowPaths']
query_file = f'{codeql_src_path}/dataFlows.ql'

toReplace = '<FunctionName>'
with open(f'{codeql_src_path}/utils/Config_Template.qll', 'r') as file:
    config_template = file.read()

children = os.scandir(functions_path)
for child in children:
    print('Analyzing function', child.name)
    config = config_template.replace(toReplace, child.name)
    with open(f'{codeql_src_path}/utils/Config.qll', 'w') as file:
        file.write(config)

    # Run the CodeQL query using subprocess.run and capture the output
    # result = subprocess.run(['codeql', 'query', 'run', query_file, '--database', codeql_db_path,
    #                         '--threads', '0', '--output', f'{root_path}/output/{child.name}.json'], capture_output=True)

    for query_file in queries:
        query = f'codeql database analyze --output={root_path}/output/{child.name}_{query_file}.sarif --format=sarifv2.1.0 {codeql_db_path} {codeql_src_path}/{query_file}.ql'
        print('Running Query: ', query)
        # result = subprocess.run([query], capture_output=True)
        result = subprocess.run(['codeql', 'database', 'analyze', '--output', f'{root_path}/output/{child.name}_{query_file}.sarif',
                                '--format', 'sarifv2.1.0', '--rerun', codeql_db_path, f'{codeql_src_path}/{query_file}.ql'], capture_output=True)
        print(result.stderr.decode())