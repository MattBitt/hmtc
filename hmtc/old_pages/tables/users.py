import time
from typing import Callable

import ipyvue
import pandas as pd
import peewee
import solara
from loguru import logger
from peewee import fn

from hmtc.components.shared.sidebar import MySidebar
from hmtc.components.tables.user_table import UserTable
from hmtc.models import User as UserModel


def parse_url_args():
    router = solara.use_router()
    level = solara.use_route_level()

    logger.debug(f"Router Parts: {router.parts}")
    logger.debug(f"Router Level: {level}")


def view_details(router, item):
    router.push(f"/user-details/{item['id']}")


@solara.component
def Page():

    router = solara.use_router()
    MySidebar(router)

    parse_url_args()

    headers = [
        {"text": "ID", "value": "id", "sortable": True, "align": "right"},
        {"text": "Username", "value": "username", "width": "30%"},
        {"text": "Email", "value": "email"},
        {"text": "Jellyfin ID", "value": "jellyfin_id"},
        {"text": "Actions", "value": "actions", "sortable": False},
    ]

    search_fields = [UserModel.username]

    with solara.Column(classes=["main-container"]):
        UserTable(
            router=router,
            headers=headers,
            base_query=UserModel.select(),
            search_fields=search_fields,
        )
