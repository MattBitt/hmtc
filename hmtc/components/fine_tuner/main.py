import solara
from hmtc.domains.video import Video

@solara.component_vue('./TimePanel.vue', vuetify=True)
def TimePanel(initialTime=1000, sectionID=18,video_duration=1000):
    pass

@solara.component
def FineTuner(video: Video):
    solara.Markdown(f"Video Fine Tuner")
    solara.Markdown(f"{video.instance.title}")
    TimePanel()