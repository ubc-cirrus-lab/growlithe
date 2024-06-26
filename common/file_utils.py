import os
from common.app_config import src_dir

"""
Create a directory if it does not exist
"""


def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


"""
Return a list of files in a directory for a specific language
"""


def get_language_files(root, language):
    result = []
    # Find all files in the directory
    for _, sub_dirs, _ in os.walk(root):
        for sub_dir in sub_dirs:
            if sub_dir == src_dir:
                # Find all files in the sub directory
                for sub_dir_path, _, files in os.walk(os.path.join(root, sub_dir)):
                    for file in files:
                        if (language == "python" and file.endswith(".py")) or (language == "javascript" and file.endswith(".js")):
                            relative_path = os.path.relpath(
                                os.path.join(sub_dir_path, file), root
                            )
                            relative_path = relative_path.replace(os.path.sep, "/")
                            result.append(relative_path)
    return result


"""
Return the list of languages found in a directory
"""
# Define a mapping of file extensions to programming languages
EXTENSION_LANGUAGE_MAP = {
    '.py': 'python',
    '.js': 'javascript',
}

def detect_languages(path):
    languages_used = set()
    for root, dirs, files in os.walk(path):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension in EXTENSION_LANGUAGE_MAP:
                languages_used.add(EXTENSION_LANGUAGE_MAP[extension])
    return languages_used