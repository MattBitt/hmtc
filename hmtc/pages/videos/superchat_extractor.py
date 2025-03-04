import solara
from loguru import logger


from hmtc.components.sectionalizer import Sectionalizer
from hmtc.components.shared import PaginationControls
from hmtc.domains.section import Section
from hmtc.domains.topic import Topic
from hmtc.domains.video import Video

refresh = solara.reactive(1)


def parse_url_args():
    router = solara.use_router()
    _id = router.parts[-1]
    if not _id.isnumeric():
        raise ValueError(f"Video ID must be an integer")
    return _id


time_cursor = solara.reactive(0)

@solara.component
def ControlPanel(video: Video):
    logger.debug(f'{video}')
    
    def find_5():
        video.extract_superchats(5)
    
    def find_all():
        video.extract_superchats()
    
    
    solara.Text(f'{video}')
    with solara.Columns([1,2,1]):
        
        with solara.Column():
            solara.Button("Find Superchats (5)", on_click=find_5, classes=['button'])
            solara.Button("Find Superchats (All)", on_click=find_all, classes=['button'])
        
        with solara.Column():
            solara.Image(video.poster(), width='500px')

        with solara.Column():
            solara.Button("click me")

@solara.component
def SuperchatList(superchats):
    logger.debug(superchats.select())
    solara.Markdown(f"Superchat Cards Go Here...")

@solara.component
def Page():
    router = solara.use_router()
    video_id = parse_url_args()
    video = Video(video_id)
    current_page = solara.use_reactive(1)
    
    per_page = 4
    
    _superchats, num_items, num_pages = video.superchats_paginated(
        current_page=current_page, per_page=per_page
    )
    
    if refresh.value > 0:
        with solara.Column(classes=["main-container"]):
            ControlPanel(video)
            SuperchatList(_superchats)
            PaginationControls(
                current_page=current_page, num_pages=num_pages, num_items=num_items
            )
