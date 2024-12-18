from hmtc.domains.series import Series
from hmtc.models import Series as SeriesModel
from hmtc.repos.base_repo import Repository


def test_empty_series(empty_db):
    c = Series()
    assert type(c.repo) == Repository


def test_series_create_and_load(empty_db, series_dict):
    created_series = Series.create(series_dict)
    assert created_series.title == series_dict["title"]
    assert created_series.start_date == series_dict["start_date"]
    assert created_series.end_date == series_dict["end_date"]
    assert created_series.id > 0

    loaded_series = Series.load(created_series.id)
    assert loaded_series.title == series_dict["title"]
    assert created_series.start_date == series_dict["start_date"]
    assert created_series.end_date == series_dict["end_date"]
    Series.delete_id(created_series.id)


def test_series_delete(seeded_db, series_dict):
    created_series = Series.create(series_dict)
    Series.delete_id(created_series.id)
    c = SeriesModel.select().where(SeriesModel.id == created_series.id).get_or_none()
    assert c is None


def test_serialize(seeded_db):
    _series = SeriesModel.select().first()
    series = Series.serialize(_series.id)
    assert series["title"] == _series.title
    assert series["start_date"] == str(_series.start_date)
    assert series["end_date"] == str(_series.end_date)


def test_get_all(seeded_db):
    all_seriess = Series.get_all()
    assert len(list(all_seriess)) == 3


def test_update_seriess(seeded_db):
    series = SeriesModel.select().first()
    orig_title = series.title
    assert series.title == "Livestreams"
    Series.update({"title": "A whole nother title", "id": series.id})
    assert SeriesModel.get_by_id(series.id).title == "A whole nother title"
    Series.update({"title": orig_title, "id": series.id})
    assert SeriesModel.get_by_id(series.id).title == orig_title
