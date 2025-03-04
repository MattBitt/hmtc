import solara
from hmtc.domains.video import Video
from hmtc.domains.section import Section
from hmtc.components.shared import PaginationControls




@solara.component
def SuperchatExtractor(video: Video):
    solara.Markdown(f"{video} - Now Paginated")

    current_page = solara.use_reactive(1)
    # 2/21/25
    # having issues with frontend updating between page loads
    # essentially disabling pagination here
    # at least until a video has > 16 sections...
    per_page = 16
    
    sections, num_sections, num_pages = video.sections_paginated(
        current_page=current_page, per_page=per_page
    )

    

    PaginationControls(
        current_page=current_page, num_pages=num_pages, num_items=num_sections
    )
