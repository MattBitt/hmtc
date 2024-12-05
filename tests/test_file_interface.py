from pathlib import Path

from hmtc.schemas.file_interface import FileInterface


def test_file_interface():
    fi = FileInterface.from_filename(Path("tests/test_file_interface.py"))
