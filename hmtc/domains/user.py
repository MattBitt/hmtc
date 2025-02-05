from typing import Any, Dict

from loguru import logger

from hmtc.domains.base_domain import BaseDomain
from hmtc.models import User as UserModel
from hmtc.repos.user_repo import UserRepo


class User(BaseDomain):
    model = UserModel
    repo = UserRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "initials": self.instance.username[:1],
            "username": self.instance.username,
            "email": self.instance.email,
            "is_admin": self.instance.is_admin,
            "jellyfin_id": self.instance.jellyfin_id,
        }

    @staticmethod
    def hash_password(text_password):
        return text_password + "_hashed"

    @classmethod
    def create(cls, user_data):

        existing = (
            UserModel.select()
            .where(UserModel.username == user_data["username"])
            .get_or_none()
        )
        if existing is None:
            _password = user_data.pop("password")
            user_data["hashed_password"] = User.hash_password(_password)
            new_user = cls.model.create(**user_data)
            logger.success(f"New user {new_user} created!")
            return cls(new_user)
        else:
            logger.error(f"User {existing} already exists. Can't create")
