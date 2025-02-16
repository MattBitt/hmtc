import solara
from loguru import logger
from hmtc.domains.video import Video
from hmtc.components.shared.pagination_controls import PaginationControls

@solara.component_vue("./TimePanel.vue", vuetify=True)
def TimePanel(initialTime=1000, sectionID=18, video_duration=1000, event_update_time=None):
    pass

@solara.component
def NotCompletedSectionCard(section):

    def update_time(start_or_end, data):
        logger.debug(f"Updating section {section} {start_or_end}")
        logger.debug(f"with data: {data}")    

    with solara.Columns():
        TimePanel(initialTime=section.start, event_update_time=lambda x: update_time("start", x))
        TimePanel(initialTime=section.end,event_update_time=lambda x: update_time("end", x))

@solara.component
def CompletedSectionCard(section):
    with solara.Card():
            with solara.Columns():
                solara.Text(f"Finished!!!")
                
@solara.component
def SectionCard(section):


    if section.fine_tuned:
        CompletedSectionCard(section)
    else:
        NotCompletedSectionCard(section)
    with solara.Row(justify="center"):
        solara.Button(label=f"Mark Completed {section.fine_tuned}", classes=['button'])
    


@solara.component
def FineTuner(video: Video):
    current_page = solara.use_reactive(1)
    per_page = 3
    solara.Markdown(f"Video Fine Tuner")
    solara.Markdown(f"{video.instance.title}")
    sections, num_sections, num_pages = video.sections_paginated(current_page=current_page, per_page=per_page)
    for sect in sections:
        with solara.Card():
            SectionCard(sect)
            
    PaginationControls(current_page=current_page, num_pages=num_pages, num_items=num_sections)