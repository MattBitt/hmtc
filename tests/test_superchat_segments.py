from pathlib import Path

from hmtc.config import init_config
from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.models import Video as VideoModel
from hmtc.schemas.file import FileManager
from hmtc.schemas.superchat import Superchat as SuperchatItem
from hmtc.schemas.superchat_segment import SuperchatSegment as SuperchatSegmentItem
from hmtc.utils.opencv.image_manager import ImageManager
from hmtc.utils.opencv.superchat_ripper import SuperChatRipper

config = init_config()

WORKING = Path(config["paths"]["working"])

TARGET_PATH = WORKING / "files_created_by_testing"
TARGET_PATH.mkdir(exist_ok=True)


def test_superchat_segments():
    vid = VideoModel.create(
        title="Some other stuff",
        description="Blah blah blah",
        youtube_id="7846157486",
        upload_date="2024-01-01",
        duration=1200,
    )

    segment1 = (SuperchatSegmentModel.create(start_time=0, end_time=10, video=vid),)

    segment2 = SuperchatSegmentModel.create(start_time=10, end_time=20, video=vid)


def test_superchat_segment_item(test_ww116_images, test_ww_video_file):
    tp = TARGET_PATH / "superchat_segment_item"
    tp.mkdir(exist_ok=True)

    new_vid = VideoModel.create(
        title="Test Video in superchat_segment_item",
        description="This is a test video",
        youtube_id="abcdefghijkl",
        upload_date="2021-01-01",
        duration=1200,
    )
    FileManager.add_path_to_video(path=test_ww_video_file, video=new_vid)
    counter = 0
    has_superchats, _ = test_ww116_images
    editor = ImageManager(has_superchats[0])
    sc = SuperChatRipper(editor.image)
    sc_image, found = sc.find_superchat()
    assert found
    superchat = SuperchatItem(
        frame_number=counter,
        video=new_vid,
        image=ImageManager(sc_image).image,
    )
    superchat.save_to_db()
    superchat.write_image(tp / f"testing_superchat.jpg")
    segment1 = SuperchatSegmentModel.create(start_time=0, end_time=10, video=new_vid)
    sg1 = SuperchatSegmentItem.from_model(segment1)
    segment2 = SuperchatSegmentModel.create(start_time=10, end_time=20, video=new_vid)
    sg2 = SuperchatSegmentItem.from_model(segment2)
    assert sg1.start_time == 0
    assert sg1.end_time == 10
    assert sg1.video_id == new_vid.id
    assert sg2.start_time == 10
    assert sg2.end_time == 20

    SuperchatSegmentItem.delete_id(segment1.id)
    SuperchatSegmentItem.delete_id(segment2.id)
    assert SuperchatSegmentModel.select().count() == 0


def test_combine_segments(test_ww116_images, test_ww_video_file2):

    tp = TARGET_PATH / "superchat_segment_item"
    tp.mkdir(exist_ok=True)

    new_vid = VideoModel.create(
        title="Test Video in test_combine_segments",
        description="This is a test_combine_segments test_combine_segments",
        youtube_id="test_combine_segments",
        upload_date="2021-01-01",
        duration=1200,
    )
    FileManager.add_path_to_video(path=test_ww_video_file2, video=new_vid)
    counter = 0
    has_superchats, _ = test_ww116_images
    editor = ImageManager(has_superchats[0])
    sc = SuperChatRipper(editor.image)
    sc_image, found = sc.find_superchat()
    assert found
    superchat = SuperchatItem(
        frame_number=counter,
        video=new_vid,
        image=ImageManager(sc_image).image,
    )
    superchat.save_to_db()
    superchat.write_image(tp / f"testing_superchat.jpg")

    segment1 = SuperchatSegmentModel.create(start_time=0, end_time=10, video=new_vid)
    segment2 = SuperchatSegmentModel.create(start_time=10, end_time=20, video=new_vid)

    sg1 = SuperchatSegmentItem.combine_segments(segment1, segment2)
    assert sg1.start_time == 0
    assert sg1.end_time == 20
    assert sg1.video_id == new_vid.id
