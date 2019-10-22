from App.Common.utils import get_files
import os 

FILES_DIR = os.path.join(
    "C:/Users/w1jtoo/Desktop/programming/python/tasks/Foogle/Tests/env/files"
)

DATEBASE = os.path.join(
    "C:/Users/w1jtoo/Desktop/programming/python/tasks/Foogle/Tests/env/foogletempbase.db"
)


def test_false():
    files = get_files(FILES_DIR)
    assert files