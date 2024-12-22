from hmtc.domains.base_domain import BaseDomain
from hmtc.models import User as UserModel
from hmtc.repos.user_repo import UserRepo
from typing import Dict, Any


class User(BaseDomain):
    model = UserModel
    repo = UserRepo()

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.instance.id,
            "username": self.instance.username,
            "email": self.instance.email,
            "hashed_password": self.instance.hashed_password,
            "jellyfin_id": self.instance.jellyfin_id,
        }
