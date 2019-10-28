import os
import time

def get_files(path_name: str) -> list:
    result = []
    for f in os.listdir(path_name):
        if os.path.isfile(os.path.join(path_name, f)):
            result.append(os.path.join(path_name, f))
    return result


def is_text_file(path: str) -> bool:
    pass

def timeme(method):
    def wrapper(*args, **kw):
        start_time = int(round(time.time() * 1000))
        result = method(*args, **kw)
        end_time = int(round(time.time() * 1000))
        print((end_time - start_time)/1000, 's')
        return result
    return wrapper