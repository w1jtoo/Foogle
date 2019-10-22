from App.Common.utils import get_files
import os 

FILES_DIR = os.path.abspath(
    "Tests/environment/files"
)

DATEBASE = os.path.abspath(
    "Tests/environment/foogletempbase.db"
)


def test_false():
    files = get_files(FILES_DIR)
    assert files