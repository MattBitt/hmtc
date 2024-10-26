import solara

from hmtc.components.shared.sidebar import MySidebar


@solara.component_vue("../components/auth/LoginPage.vue")
def LoginPage():
    pass


@solara.component
def Page():
    router = solara.use_router()
    MySidebar(router=router)
    LoginPage()
