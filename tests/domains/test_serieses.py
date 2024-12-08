from hmtc.domains.series import Series
from hmtc.models import Series as SeriesModel
from hmtc.repos.base_repo import Repository


def test_empty_series():
    c = Series()
    assert type(c.repo) == Repository


def test_series_create_and_load(series_dict1):
    created_series = Series.create(series_dict1)
    assert created_series.title == series_dict1["title"]
    assert created_series.start_date == series_dict1["start_date"]
    assert created_series.end_date == series_dict1["end_date"]
    assert created_series.id > 0

    loaded_series = Series.load(created_series.id)
    assert loaded_series.title == series_dict1["title"]
    assert created_series.start_date == series_dict1["start_date"]
    assert created_series.end_date == series_dict1["end_date"]


def test_series_delete(series_dict1):
    created_series = Series.create(series_dict1)
    Series.delete_id(created_series.id)
    c = SeriesModel.select().where(SeriesModel.id == created_series.id).get_or_none()
    assert c is None


def test_serialize(series_dict1):
    new_id = Series.create(series_dict1)
    s = Series.serialize(new_id)
    assert s["title"] == series_dict1["title"]
    assert str(s["start_date"]) == series_dict1["start_date"]
    assert str(s["end_date"]) == series_dict1["end_date"]


def test_get_all(series_dicts):
    for sd in series_dicts:
        Series.create(sd)

    all_seriess = Series.get_all()
    assert len(list(all_seriess)) == 3


def test_update_seriess(series_dict1):
    new_id = Series.create(series_dict1)
    series = Series.load(new_id)
    assert series.title == series_dict1["title"]
    Series.update({"title": "A whole nother title", "id": new_id})
    assert SeriesModel.get_by_id(new_id).title == "A whole nother title"
