import solara
import solara.lab
from loguru import logger

from hmtc.components.shared import Chip, InputAndDisplay, MySpinner
from hmtc.components.video.jf_panel import JFPanel
from hmtc.domains.track import Track
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.utils.jellyfin_functions import (
    can_ping_server,
    get_user_favorites,
    get_user_session,
)



@solara.component
def Page():
    

    sess = get_user_session()['NowPlayingItem']
    JFPanel(video=None)
    solara.Markdown(f"wow") 
    
