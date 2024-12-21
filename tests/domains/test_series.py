from hmtc.domains.series import Series
from hmtc.models import Series as SeriesModel


def test_series_create_and_load(series_dicts):
    sd = series_dicts[0]
    created_series = Series.create(sd)
    assert created_series.instance.title == sd["title"]
    assert created_series.instance.id > 0

    loaded_series = Series.load(created_series.instance.id)
    assert loaded_series.instance.title == sd["title"]
    created_series.delete()


def test_series_create_no_title(series_dicts):
    sd = series_dicts[0]
    del sd["title"]
    try:
        Series.create(sd)
        assert False
    except Exception as e:
        assert "null value in column" in str(e)
        assert 1 == 1


def test_get_by_id(series_dicts):
    sd = series_dicts[1]
    created_series = Series.create(sd)
    loaded_series = Series.get_by(id=created_series.instance.id)
    assert loaded_series.instance.title == sd["title"]
    created_series.delete()


def test_get_by_title(series_dicts):
    sd = series_dicts[1]
    created_series = Series.create(sd)
    loaded_series = Series.get_by(title=created_series.instance.title)
    assert loaded_series.instance.title == sd["title"]
    created_series.delete()


def test_select_where(series_dicts):
    sd1 = series_dicts[1]
    sd2 = series_dicts[2]
    series1 = Series.create(sd1)
    series2 = Series.create(sd2)

    series_query = Series.select_where(title=series1.instance.title)
    assert len(series_query) == 1
    series_item = Series(series_query[0].instance.id)
    assert series_item.instance.title == sd1["title"]
    loaded_series = series_query[0]
    assert loaded_series.instance.title == sd1["title"]
    series1.delete()
    series2.delete()


def test_update_series(series_dicts):
    sd = series_dicts[2]
    series = Series.create(sd)
    new_series = series.update({"title": "New Title"})
    assert new_series.instance.title == "New Title"

    series_from_db = (
        SeriesModel.select().where(SeriesModel.id == series.instance.id).get()
    )
    assert series_from_db.title == "New Title"
    series.delete()


def test_series_delete(series_dicts):
    sd = series_dicts[1]
    created_series = Series.create(sd)
    created_series.delete()
    s = (
        SeriesModel.select()
        .where(SeriesModel.id == created_series.instance.id)
        .get_or_none()
    )
    assert s is None


def test_serialize(series_dicts):
    sd = series_dicts[2]
    series = Series.create(sd)
    s = series.serialize()
    assert s["title"] == sd["title"]
    series.delete()


def test_count(series_dicts):
    sd1 = series_dicts[0]
    sd2 = series_dicts[1]
    sd3 = series_dicts[2]

    assert Series.count() == 0
    Series.create(sd1)
    Series.create(sd2)
    Series.create(sd3)
    assert Series.count() == 3

    for series_dict in series_dicts:
        series = Series.get_by(title=series_dict["title"])
        series.delete()

    assert Series.count() == 0
