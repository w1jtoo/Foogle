import os


def get_files(path_name: str) -> list:
    result = []
    for f in os.listdir(path_name):
        if os.path.isfile(os.path.join(path_name, f)):
            result.append(os.path.join(path_name, f))
    return result
