from hmtc.models import User as UserModel
from hmtc.repos.base_repo import Repository


def UserRepo():
    return Repository(
        model=UserModel,
        label="User",
    )
