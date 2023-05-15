import json


def get_query_results(results_file):
    with open(results_file, "r") as f:
        sarif_log = json.load(f)
    results = sarif_log["runs"][0]["results"]
    return results


def get_variable(location):
    file_name = location["physicalLocation"]["artifactLocation"]["uri"]
    start_line = location["physicalLocation"]["region"]["startLine"]
    start_column = location["physicalLocation"]["region"]["startColumn"]
    if "endLine" in location["physicalLocation"]["region"]:
        end_line = location["physicalLocation"]["region"]["endLine"]
    else:
        end_line = start_line
    end_column = location["physicalLocation"]["region"]["endColumn"]
    variable = read_variable(file_name, start_line, start_column, end_line, end_column)
    return variable


def read_variable(file_name, line_start, offset_start, line_end, offset_end):
    variable = ""
    with open(f"../src/{file_name}", "r") as f:
        lines = f.readlines()
        if line_start == line_end:
            variable = lines[line_start - 1][offset_start - 1 : offset_end - 1]
        else:
            variable = lines[line_start - 1][offset_start - 1 :]
            for i in range(line_start, line_end - 1):
                variable += lines[i]
            variable += lines[line_end - 1][:offset_end]
    return variable
