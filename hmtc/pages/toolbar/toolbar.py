import solara
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.utils.version_manager import get_version

# program version
VERSION = f"v{get_version()}"


@solara.component_vue("./AvatarMenu.vue")
def AvatarMenu(user, version, event_logout_user):
    pass


@solara.component
def MainToolbar(user):

    def logout_user(*args):
        logger.debug(args)
        user.set(None)

    with solara.Row(style={"background-color": Colors.PRIMARY}):
        with solara.Link(f"/"):
            solara.Button(icon_name="mdi-home", icon=True)
        with solara.Link(f"/admin/dashboards/domains"):
            solara.Button(
                icon_name="mdi-google-circles-extended",
                icon=True,
            )
        with solara.Link(f"/admin/dashboards/files"):
            solara.Button(
                icon_name="mdi-folder",
                icon=True,
            )
        with solara.Link(f"/admin/settings"):
            solara.Button(
                icon_name="mdi-cogs",
                icon=True,
            )
        with solara.Link(f"/api/videos"):
            solara.Button(
                icon_name="mdi-video",
                icon=True,
            )

        if user.value:
            AvatarMenu(
                user=user.value.serialize(),
                version=VERSION,
                event_logout_user=logout_user,
            )
