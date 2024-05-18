import ipywidgets
import solara

url = "https://user-images.githubusercontent.com/1765949/240697327-25b296bd-72c6-4412-948b-2d37e8196260.mp4"


@solara.component
def Page():
    ipywidgets.Video.element(value=url.encode("utf8"), format="url", width=500)
