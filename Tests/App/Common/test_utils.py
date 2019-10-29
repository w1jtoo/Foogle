from App.Common.utils import get_files, filter_files
import os

FILES_DIR = os.path.abspath("Tests/environment/files")

DATEBASE = os.path.abspath("Tests/environment/foogletempbase.db")


def test_sould_not_be_empty():
    files = get_files(FILES_DIR)
    assert files

def test_files_should_be_in_getfiles():
    files = get_files(FILES_DIR)
    assert len(files) == 8

def test_should_included_txt_files():
    files = filter_files(get_files(FILES_DIR), ["text/plain"])
    assert len(files) == 6

def test_should_empty_types():
    files = filter_files(get_files(FILES_DIR), [])
    assert not files