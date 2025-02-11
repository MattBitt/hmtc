import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.assets.icons.icon_repo import Icons
from hmtc.utils.version_manager import get_version

# program version
VERSION = f"v{get_version()}"


@solara.component_vue("./AvatarMenu.vue")
def AvatarMenu(user, version, event_logout_user):
    pass


@solara.component
def MainToolbar(user, logged_in):

    def logout_user(*args):
        logger.debug(args)
        user.set(None)
        logged_in.set(False)

    with solara.Row(style={"background-color": Colors.PRIMARY}):
        with solara.Link(f"/"):
            solara.Button(icon_name=Icons.HOME.value, icon=True)
        with solara.Link(f"/admin/dashboards/domains"):
            solara.Button(
                icon_name=Icons.DOMAIN.value,
                icon=True,
            )
        with solara.Link(f"/admin/dashboards/files"):
            solara.Button(
                icon_name=Icons.FILE.value,
                icon=True,
            )
        with solara.Link(f"/admin/settings"):
            solara.Button(
                icon_name=Icons.SETTINGS.value,
                icon=True,
            )
        with solara.Link(f"/api/videos"):
            solara.Button(
                icon_name=Icons.VIDEO.value,
                icon=True,
            )

        if user.value:
            AvatarMenu(
                user=user.value.serialize(),
                version=VERSION,
                event_logout_user=logout_user,
            )
