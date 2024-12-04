from hmtc.real_world_tests import BirdManager
import peewee
from loguru import logger
import pytest


def test_create_robin(robin_bm):

    assert robin_bm.bird.species == "robin"
    assert robin_bm.bird.weight == 13
    assert robin_bm.bird.color == "red"


def test_failed_create_robin():
    try:
        bm = BirdManager.create(weight=13, color="red")
        assert False
    except Exception as e:
        assert True


def test_create_bluejay(bluejay_bm):
    assert bluejay_bm.bird.species == "blue jay"
    assert bluejay_bm.bird.weight == 20
    assert bluejay_bm.bird.color == "blue"


def test_create_bird_duplicate(robin_bm):
    # robin_bm is a fixture that creates a bird with species="robin"
    try:
        bm = BirdManager.create(species="robin", weight=42, color="red")
    except peewee.IntegrityError as e:
        assert "violates unique constraint" in str(e)


def test_create_bird_file_from_path(robin_bm, test_image_filename):
    bm = robin_bm
    bm.add_file(test_image_filename)
    assert len(bm.files) == 1


def test_create_manager_from_bird_file_from_id(test_image_filename):
    bm = BirdManager.create(species="robin", weight=19, color="fdsa")


def test_add_file_fails():
    bm = BirdManager.create(species="robin", weight=19, color="fdsa")

    try:
        # this file doesn't exist so the above should throw an error
        bm.add_file("test.jpg")

    except Exception as e:
        assert True

    assert len(bm.bird.files) == 0


def test_add_file_succeeds(test_image_filename):
    bm = BirdManager.create(species="robin", weight=19, color="fdsa")
    bm.add_file("test.jpg")
    assert len(bm.bird.files) == 1
    assert bm.bird.files[0].filename == "test.jpg"
    assert bm.bird.files[0].file_type.title == "poster"
    assert bm.bird.files[0].path == "somepath"
    assert bm.bird.files[0].id is not None
