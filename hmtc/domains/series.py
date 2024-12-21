from hmtc.models import Series as SeriesModel
from hmtc.domains.base_domain import BaseDomain


class Series(BaseDomain):
    model = SeriesModel

    def __init__(self, item_id):
        super().__init__(item_id)
