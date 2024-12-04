def test_connect_to_db(db):
    db_instance, config = db
    assert db_instance is not None
    assert len(db_instance.get_tables()) > 0
