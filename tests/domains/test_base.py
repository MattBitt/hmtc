from hmtc.domains.base import Repository


def test_empty_base_domain():
    x = Repository()
    assert x is not None
