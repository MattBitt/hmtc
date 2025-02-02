import solara

from hmtc.utils.version_manager import get_version

# program version
VERSION = f"v{get_version()}"


@solara.component
def MainToolbar(router, user):
    with solara.Row():
        with solara.Link(f"/"):
            solara.Button(icon_name="mdi-home", icon=True)
        with solara.Link(f"/dashboards/domains"):
            solara.Button(
                icon_name="mdi-google-circles-extended",
                icon=True,
            )
        with solara.Link(f"/dashboards/files"):
            solara.Button(
                icon_name="mdi-folder",
                icon=True,
            )
        with solara.Link(f"/utils/settings"):
            solara.Button(
                icon_name="mdi-cogs",
                icon=True,
            )
        if True:  # logged_out
            solara.Button(
                icon_name="mdi-login",
                on_click=lambda: router.push("/login"),
                icon=True,
            )
        else:
            solara.Button(
                icon_name="mdi-logout",
                on_click=lambda: router.push("/logout"),
                icon=True,
            )

        solara.Text(f"{VERSION}", classes=["version-number"])
        if user.value:
            solara.Text(
                f"Logged in as {user.value.username} as {'admin' if user.value.admin else 'user'}"
            )
            with solara.Tooltip("Logout"):
                solara.Button(
                    icon_name="mdi-logout",
                    icon=True,
                    on_click=lambda: user.set(None),
                )
        else:
            solara.Text("Not logged in")
