from peewee import DoesNotExist, Model


class BaseDomain:
    model = None
    repo = None
    fm = None

    def __init__(self, item_id=None):
        if item_id:
            self.instance = self.repo.get_by_id(item_id)
        else:
            self.instance = None

    @classmethod
    def create(cls, data):
        instance = cls.model.create(**data)
        return cls(instance)

    def save(self):
        if self.instance:
            self.instance.save()

    def delete(self):
        if self.instance:
            self.instance.delete_instance()

    def update(self, data) -> "BaseDomain":
        for key, value in data.items():
            setattr(self.instance, key, value)
        self.save()
        return self

    def serialize(self):
        return self.instance.my_dict()

    @classmethod
    def load(cls, instance_id):
        try:
            instance = cls.model.get(cls.model.id == instance_id)
            return cls(instance)
        except DoesNotExist:
            return None

    @classmethod
    def get_by(cls, **kwargs):
        try:
            instance = cls.model.get(**kwargs)
            return cls(instance)
        except DoesNotExist:
            return None

    @classmethod
    def select_where(cls, **kwargs):
        query = cls.model.query_from_kwargs(**kwargs)
        return [cls(instance) for instance in query]

    @classmethod
    def count(cls):
        return cls.model.select().count()
