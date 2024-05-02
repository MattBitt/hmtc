import pytest
from hmtc.models import Video


def test_add():
    assert 1 == 1


def test_db2():
    Video.create_table()
    # v = Video.create(name="test")
    vids = [v.name for v in Video.select()]
    assert vids is not []


#     db = create_tables()
#     yield db
#     db.close()
#     assert 1 == 1
