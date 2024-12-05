from hmtc.real_world_tests import BirdManager
import peewee
from loguru import logger
import pytest


def test_create_robin(robin_bm):
    assert robin_bm.bird_model.species == "robin"
    assert robin_bm.bird_model.weight == 13
    assert robin_bm.bird_model.color == "red"


def test_failed_create_robin():
    # needs species as a required argument
    try:
        bm = BirdManager.create(weight=13, color="red")
        assert False
    except Exception as e:
        pass


def test_create_bluejay(bluejay_bm):
    assert bluejay_bm.bird_model.species == "blue jay"
    assert bluejay_bm.bird_model.weight == 20
    assert bluejay_bm.bird_model.color == "blue"


def test_delete_bird(robin_bm):
    robin_bm.delete_me()
    try:
        # should fail because the bird was deleted
        BirdManager.load(species="robin")
        assert False
    except Exception as e:
        pass


def test_create_bird_duplicate(robin_bm):
    # robin_bm is a fixture that creates a bird with species="robin"
    try:
        bm = BirdManager.create(species="robin", weight=42, color="red")
    except peewee.IntegrityError as e:
        assert "violates unique constraint" in str(e)
