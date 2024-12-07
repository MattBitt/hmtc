from hmtc.repos.base_repo import Repository
from hmtc.models import BaseModel


def test_base_repository():
    repo = Repository(model=BaseModel, label="BaseModel")
    assert repo.model == BaseModel
    assert repo.label == "BaseModel"
