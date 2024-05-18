import solara

from hmtc.models import Video

yt_id = solara.reactive("")


@solara.component
def Page():
    def add_video():
        Video.create_from_yt_id(yt_id.value)

    with solara.Card():
        solara.InputText(
            label="Enter YouTube ID",
            value=yt_id,
            continuous_update=False,
        )
        solara.Button("Add Video to Database", on_click=add_video)
        solara.Markdown("Add Video")
