from hmtc.domains.series import Series
from hmtc.models import Series as SeriesModel
from hmtc.repos.base_repo import Repository

testing_series_dict = {
    "id": 807,
    "title": "Some Test Series Title",
    "start_date": "2021-01-01",
    "end_date": "2021-01-01",
}


def test_empty_series(empty_db):
    c = Series()
    assert type(c.repo) == Repository


def test_series_create_and_load(empty_db):
    created_series = Series.create(testing_series_dict)
    assert created_series.title == testing_series_dict["title"]
    assert created_series.start_date == testing_series_dict["start_date"]
    assert created_series.end_date == testing_series_dict["end_date"]
    assert created_series.id > 0

    loaded_series = Series.load(created_series.id)
    assert loaded_series.title == testing_series_dict["title"]
    assert created_series.start_date == testing_series_dict["start_date"]
    assert created_series.end_date == testing_series_dict["end_date"]
    Series.delete_id(created_series.id)


def test_series_delete(seeded_db):
    created_series = Series.create(testing_series_dict)
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
    SERIES_ID = 1
    series = Series.load(SERIES_ID)
    orig_title = series.title
    assert series.title == "On the Hiking Trail"
    Series.update({"title": "A whole nother title", "id": 1})
    assert SeriesModel.get_by_id(SERIES_ID).title == "A whole nother title"
    Series.update({"title": orig_title, "id": SERIES_ID})
    assert SeriesModel.get_by_id(SERIES_ID).title == orig_title
