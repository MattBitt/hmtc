from pathlib import Path
from unittest.mock import MagicMock

import pytest

from hmtc.models import Channel as ChannelModel
from hmtc.models import ChannelFile
from hmtc.repos.base_repo import Repository
from hmtc.utils.file_manager import FileManager

# these were ai generated tests. i like the style, but confused if
# they are actually testing anything


@pytest.fixture
def mock_model():
    return MagicMock(spec=ChannelModel)


@pytest.fixture
def mock_file_model():
    return MagicMock(spec=ChannelFile)


@pytest.fixture
def temp_path(tmp_path):
    return tmp_path


@pytest.fixture
def repo(mock_model, mock_file_model, temp_path):
    return Repository(
        model=mock_model,
        label="TestChannelRepo",
    )


@pytest.fixture
def file_manager(mock_file_model, temp_path):
    return FileManager(
        model=mock_file_model,
        filetypes=["poster", "thumbnail", "info"],
        path=temp_path,
    )


def test_create_item(repo, mock_model):
    data = {"title": "test"}
    repo.create_item(data)
    mock_model.create.assert_called_once_with(**data)


def test_delete_item(repo, mock_model):
    item_id = 1
    repo.delete_by_id(item_id)
    mock_model.delete_by_id.assert_called_once_with(item_id)


def test_add_file(repo, file_manager, mock_file_model, temp_path):
    item = MagicMock()
    file_path = temp_path / "test.txt"
    file_path.touch()
    file_manager.add_file(item, file_path)
    mock_file_model.create.assert_called_once()
