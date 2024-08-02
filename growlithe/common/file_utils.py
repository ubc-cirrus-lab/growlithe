import os
import ast


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


def get_language_files(root, language, src_dir):
    """
    Retrieves a list of file paths for a specific programming language within a given directory.
    Parameters:
        root (str): The root directory to search for files.
        language (str): The programming language to filter the files by.
        src_dir (str): The subdirectory within the root directory to search for files.
    Returns:
        list: A list of file paths that match the specified programming language within the given directory.
    """
    result = []
    # Find all files in the directory
    for _, sub_dirs, _ in os.walk(root):
        for sub_dir in sub_dirs:
            if sub_dir == src_dir:
                # Find all files in the sub directory
                for sub_dir_path, _, files in os.walk(os.path.join(root, sub_dir)):
                    for file in files:
                        if (language == "python" and file.endswith(".py")) or (
                            language == "javascript" and file.endswith(".js")
                        ):
                            relative_path = os.path.relpath(
                                os.path.join(sub_dir_path, file), root
                            )
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


def save_files(graph):
    """
    Save the files associated with each function in the graph.

    Parameters:
    - graph: The graph containing the functions.

    Returns:
    None
    """
    for function in graph.functions:
        os.makedirs(os.path.dirname(function.growlithe_function_path), exist_ok=True)
        with open(function.growlithe_function_path, "w") as f:
            f.write(ast.unparse(ast.fix_missing_locations(function.code_tree)))
