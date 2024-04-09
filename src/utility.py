import json
import os
import hashlib


class IDGenerator:
    id = 0

    @staticmethod
    def get_id():
        IDGenerator.id += 1
        return IDGenerator.id


def get_query_results(results_file):
    with open(results_file, "r") as f:
        sarif_log = json.load(f)
    results = sarif_log["runs"][0]["results"]
    return results


def get_string_from_location(location, app_src_path):
    file_name = location["physicalLocation"]["artifactLocation"]["uri"]
    start_line = location["physicalLocation"]["region"]["startLine"]
    start_column = location["physicalLocation"]["region"]["startColumn"]
    if "endLine" in location["physicalLocation"]["region"]:
        end_line = location["physicalLocation"]["region"]["endLine"]
    else:
        end_line = start_line
    end_column = location["physicalLocation"]["region"]["endColumn"]
    file_path = os.path.join(app_src_path, file_name)
    variable = read_location(file_path, start_line, start_column, end_line, end_column)
    return variable


def read_location(file_path, line_start, offset_start, line_end, offset_end):
    variable = ""
    with open(file_path, "r") as f:
        lines = f.readlines()
        if line_start == line_end:
            variable = lines[line_start - 1][offset_start - 1 : offset_end - 1]
        else:
            variable = lines[line_start - 1][offset_start - 1 :]
            for i in range(line_start, line_end - 1):
                variable += lines[i]
            variable += lines[line_end - 1][:offset_end]
    return variable


def get_rel_path(file_name):
    dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(dir, file_name)
    return path


def get_sorted_array_hash(arr):
    sorted_arr = sorted(arr)
    # arr_string = ','.join(sorted_arr)
    hash_object = hashlib.sha256(sorted_arr.encode())
    hash_value = hash_object.hexdigest()
    return hash_value


def add_assertion(input_file, physical_location, policy):
    with open(input_file, "r") as file:
        lines = file.readlines()

    target_line_number = physical_location["region"]["startLine"]

    target_indent = ""
    for char in lines[target_line_number - 1]:
        if char.isspace():
            target_indent += char
        else:
            break

    assert_line = (
        f"{target_indent}# ========== Growlithe ==========\n"
        + f"{target_indent}import policyLib\n"
        + f"{target_indent}assert {policy}, 'Policy Violation'\n"
        + f"{target_indent}# ========== Growlithe ==========\n"
    )

    lines.insert(target_line_number - 1, assert_line)

    with open(input_file + ".annotated", "w") as file:
        file.writelines(lines)

def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)