from typing import Any, Dict, List, Optional, Type, TypeVar

from peewee import DoesNotExist, Model

T = TypeVar("T", bound="BaseDomain")


class BaseDomain:
    model = None
    repo = None
    fm = NotImplementedError("FileManager not implemented")

    def __init__(self, item_id: Optional[int] = None):
        if item_id and self.repo is not None:
            self.instance = self.repo.get_by_id(item_id)
        else:
            self.instance = None

    @classmethod
    def create(cls: Type[T], data: Dict[str, Any]) -> T:
        instance = cls.model.create(**data)
        return cls(instance)

    def save(self) -> None:
        if self.instance:
            self.instance.save()

    def delete(self) -> None:
        if self.instance:
            self.instance.delete_instance()

    def update(self, data: Dict[str, Any]) -> "BaseDomain":
        for key, value in data.items():
            setattr(self.instance, key, value)
        self.save()
        return self

    def serialize(self) -> Dict[str, Any]:
        return self.instance.my_dict()

    @classmethod
    def load(cls: Type[T], instance_id: int) -> Optional[T]:
        try:
            instance = cls.model.get(cls.model.id == instance_id)
            return cls(instance)
        except DoesNotExist:
            return None

    @classmethod
    def get_by(cls: Type[T], **kwargs: Any) -> Optional[T]:
        try:
            instance = cls.model.get(**kwargs)
            return cls(instance)
        except DoesNotExist:
            return None

    @classmethod
    def select_where(cls: Type[T], **kwargs: Any) -> List[T]:
        query = cls.model.query_from_kwargs(**kwargs)
        return [cls(instance) for instance in query]

    @classmethod
    def count(cls) -> int:
        return cls.model.select().count()
