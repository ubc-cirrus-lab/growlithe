import os
import csv
import argparse

BENCHMARK_PATH = "./src"
QUERIES = ['file', 'requests', 'socket', 'boto3']


class Handler:
    def __init__(self, name, script, function):
        self.name = name
        self.script = script
        self.function = function
        self.file_path = None

def search_directory(base, directory, script):
    for root, dirs, files in os.walk(base):
        for dir in dirs:
            directory_name = directory.lower().replace("_", "").replace("-", "")
            dir_name = dir.lower().replace("_", "").replace("-", "")
            if directory_name in dir_name or dir_name in directory_name:
                for file in os.listdir(os.path.join(root, dir)):
                    script_name = script.lower().replace("_", "").replace("-", "")
                    file_name = file.lower().replace("_", "").replace("-", "")
                    if script_name in file_name or file_name in script_name:
                        return os.path.abspath(os.path.join(root, dir, file))

def main(handler_file):
    handlers = []
    with open(handler_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            handlers.append(Handler(row[0], row[1], row[2]))
    for handler in handlers:
        file_path = search_directory(BENCHMARK_PATH, handler.name, handler.script)
        handler.file_path = file_path
        create_queries(handler)

def create_queries(handler):
    for query in QUERIES:
        with open(f'query_templates/{query}.ql', 'r') as f:
            query_template = f.read()
            query_text = query_template.replace("FUNCTION_NAME", handler.function)\
                    .replace("SCRIPT_PATH", handler.file_path)\
                    .replace("ID", handler.name)
            filename = f'queries/{handler.name}/{query}.ql'
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                f.write(query_text)
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('handler_file', help = 'CSV file containing handlers')
    args = parser.parse_args()
    

    main(args.handler_file)