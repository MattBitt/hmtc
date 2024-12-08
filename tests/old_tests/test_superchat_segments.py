from pathlib import Path

from hmtc.config import init_config
from hmtc.domains.superchat import Superchat as SuperchatItem
from hmtc.domains.superchat_segment import SuperchatSegment as SuperchatSegmentItem
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Video as VideoModel
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper

config = init_config()

WORKING = Path(config["paths"]["working"])

TARGET_PATH = WORKING / "files_created_by_testing"
TARGET_PATH.mkdir(exist_ok=True)


def test_superchat_segments(video):
    segment1 = SuperchatSegmentModel.create(start_time=0, end_time=10, video=video)

    segment2 = SuperchatSegmentModel.create(start_time=10, end_time=20, video=video)


def test_superchat_segment_item(superchat_segment1):
    tp = TARGET_PATH / "superchat_segment_item"
    tp.mkdir(exist_ok=True)

    sg1 = SuperchatSegmentItem.from_model(superchat_segment1)

    assert sg1.start_time == 0
    assert sg1.end_time == 10


def test_add_superchat_to_segment(video, superchat_image_file):
    sc = SuperchatModel.create(frame=5, video=video)
    sci = SuperchatItem.from_model(sc)
    sci.add_image(superchat_image_file)

    ss = SuperchatSegmentModel.create(start_time=0, end_time=10, video=video)
    ssi = SuperchatSegmentItem.from_model(ss)
    ssi.add_superchat(sci)

    new_ss = SuperchatSegmentModel.get_by_id(ss.id)
    assert len(new_ss.superchats) == 1
    assert new_ss.superchats[0].id == sc.id
