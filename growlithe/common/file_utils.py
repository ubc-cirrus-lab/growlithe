import os
import ast
import json
import shutil
import subprocess

from growlithe.common.logger import logger
from growlithe.common.utils import profiler_decorator


def create_dir_if_not_exists(path):
    """
    Creates a directory if it does not already exist.

    Args:
        path (str): The path of the directory to be created.

    Returns:
        None
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_language_files(root, language, src_dir, growlithe_path):
    """
    Retrieves a list of file paths for a specific programming language within a given directory,
    ignoring a specific growlithe path.

    Parameters:
        root (str): The root directory to search for files.
        language (str): The programming language to filter the files by.
        src_dir (str): The subdirectory within the root directory to search for files.
        growlithe_path (str): The specific path to ignore.

    Returns:
        list: A list of file paths that match the specified programming language within the given directory,
              excluding the specified growlithe path.
    """
    result = []
    src_full_path = os.path.join(root, src_dir)

    for dir_path, _, files in os.walk(src_full_path):
        # Skip the specific growlithe path
        if os.path.commonpath([dir_path, growlithe_path]) == growlithe_path:
            continue

        for file in files:
            if (language == "python" and file.endswith(".py")) or (
                language == "javascript" and file.endswith(".js")
            ):
                full_path = os.path.join(dir_path, file)
                relative_path = os.path.relpath(full_path, root)
                relative_path = relative_path.replace(os.path.sep, "/")
                result.append(relative_path)

    return result


# Define a mapping of file extensions to programming languages
EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
}


def detect_languages(path):
    """
    Detects the languages used in the files located at the specified path.

    Args:
        path (str): The path to the directory containing the files.

    Returns:
        set: A set of languages used in the files.

    """
    languages_used = set()
    for root, dirs, files in os.walk(path):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension in EXTENSION_LANGUAGE_MAP:
                languages_used.add(EXTENSION_LANGUAGE_MAP[extension])
    return languages_used


def get_file_extension(runtime):
    """
    Returns the file extension based on the given runtime.

    Parameters:
    - runtime (str): The runtime for which the file extension is needed.

    Returns:
    - str: The file extension corresponding to the given runtime. If the runtime is not recognized, an empty string is returned.
    """
    runtime_extensions = {
        "nodejs": ".js",
        "python": ".py",
        "ruby": ".rb",
        "java": ".java",
        "go": ".go",
        "dotnet": ".cs",
    }

    for lang, ext in runtime_extensions.items():
        if lang in runtime.lower():
            return ext
    return ""  # Default to no extension if runtime is not recognized


@profiler_decorator
def save_files(graph, growlithe_lib_path):
    """
    Save the files associated with each function in the graph.

    Parameters:
    - graph: The graph containing the functions.

    Returns:
    None
    """
    for function in graph.functions:
        logger.info(
            "Saving function %s to %s", function.name, function.growlithe_function_path
        )
        if function.runtime.startswith("python"):
            os.makedirs(
                os.path.dirname(function.growlithe_function_path), exist_ok=True
            )
            with open(function.growlithe_function_path, "w") as f:
                f.write(ast.unparse(ast.fix_missing_locations(function.code_tree)))
            local_lib_path = os.path.join(
                os.path.dirname(function.growlithe_function_path),
                "growlithe_predicates.py",
            )
            shutil.copy(growlithe_lib_path, local_lib_path)
        elif function.runtime.startswith("nodejs"):
            os.makedirs(
                os.path.dirname(function.growlithe_function_path), exist_ok=True
            )
            with open("tmp.json", "w", encoding="utf-8") as f:
                json.dump(function.code_tree, f, ensure_ascii=False, indent=4)
            subprocess.run(
                [
                    "node",
                    "growlithe/graph/adg/js/ast2file.js",
                    "tmp.json",
                    function.growlithe_function_path,
                ],
                check=True,
            )
            os.remove("tmp.json")
            # TODO: add the predicates file for nodejs
            local_lib_path = os.path.join(
                os.path.dirname(function.growlithe_function_path),
                "growlithe_predicates.js",
            )
            shutil.copy(growlithe_lib_path, local_lib_path)
        else:
            logger.error("Unsupported runtime %s", function.runtime)
            raise NotImplementedError
