import os
import subprocess

root_path = '../'
benchmark_path = f'{root_path}/benchmarks/exam/announcements/'
functions_path = f'{benchmark_path}/'
codeql_db_path = f'{benchmark_path}/codeqldb/'
codeql_src_path = f'{root_path}/static-analysis/'

output_dir = f'{benchmark_path}/output/'
os.makedirs(output_dir, exist_ok=True)

queries = ['getSources', 'getSinks', 'flowPaths', 'sinkConditions']
# queries = ['flowPaths']
# query_file = f'{codeql_src_path}/dataFlows.ql'

toReplace = 'LambdaFunctions/<FunctionName>/lambda_function'
with open(f'{codeql_src_path}/utils/Config_Template.qll', 'r') as file:
    config_template = file.read()

# children = os.scandir(functions_path)
fns = ['send_mail', 'make_announcement']
for fn in fns:
    print('Analyzing function', fn)
    config = config_template.replace(toReplace, fn)
    with open(f'{codeql_src_path}/utils/Config.qll', 'w') as file:
        file.write(config)
    for query_file in queries:
        query = f'codeql database analyze --output={output_dir}/{fn}_{query_file}.sarif --format=sarifv2.1.0 {codeql_db_path} {codeql_src_path}/{query_file}.ql'
        print('Running Query: ', query)
        # result = subprocess.run([query], capture_output=True)
        result = subprocess.run(['codeql', 'database', 'analyze', '--output', f'{output_dir}/{fn}_{query_file}.sarif',
                                '--format', 'sarifv2.1.0', '--rerun', codeql_db_path, f'{codeql_src_path}/{query_file}.ql'], capture_output=True)
        print(result.stderr.decode())