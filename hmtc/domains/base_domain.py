from peewee import Model, DoesNotExist


class BaseDomain:
    model = None
    repo = None

    def __init__(self, instance=None):
        self.instance = instance

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

    def serialize(self):
        return self.instance.my_dict()
