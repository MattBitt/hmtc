from hmtc.domains.base_domain import BaseDomain
from hmtc.models import Series as SeriesModel
from hmtc.repos.series_repo import SeriesRepo


class Series(BaseDomain):
    model = SeriesModel
    repo = SeriesRepo()

    def __init__(self, item_id):
        self.instance = self.repo.get_by_id(item_id)
        super().__init__(self.instance)
