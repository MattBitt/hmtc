from hmtc.models import Superchat as SuperchatModel
from hmtc.models import SuperchatSegment as SuperchatSegmentModel
from hmtc.schemas.superchat_segment import SuperchatSegment as SuperchatSegmentItem
from hmtc.models import Video as VideoModel


def test_superchat_segments():
    vid = VideoModel.create(
        title="Some other stuff",
        description="Blah blah blah",
        youtube_id="7846157486",
        upload_date="2024-01-01",
        duration=1200,
    )
    sc1 = SuperchatModel.create(frame_number=1, video=vid)
    segment1 = SuperchatSegmentModel.create(
        start_time=0, end_time=10, image_file_id=1, superchat=sc1
    )
    segment2 = SuperchatSegmentModel.create(
        start_time=10, end_time=20, image_file_id=2, superchat=sc1
    )
    segment3 = SuperchatSegmentModel.create(
        start_time=20, end_time=30, image_file_id=3, superchat=sc1
    )
    segment4 = SuperchatSegmentModel.create(
        start_time=30, end_time=40, image_file_id=4, superchat=sc1
    )


def test_superchat_segment_item():
    segment1 = SuperchatSegmentModel.create(start_time=0, end_time=10, image_file_id=1)
    sg1 = SuperchatSegmentItem.from_model(segment1)
    segment2 = SuperchatSegmentModel.create(start_time=10, end_time=20, image_file_id=2)
    sg2 = SuperchatSegmentItem.from_model(segment2)
    assert sg1.start_time == 0
    assert sg1.end_time == 10
    assert sg1.image_file_id == 1
    assert sg2.start_time == 10
    assert sg2.end_time == 20
    assert sg2.image_file_id == 2
    sg1.delete_id(segment1.id)
    sg2.delete_id(segment2.id)
    assert SuperchatSegmentModel.select().count() == 0


def test_combine_segments():
    segment1 = SuperchatSegmentModel.create(start_time=0, end_time=10, image_file_id=1)
    segment2 = SuperchatSegmentModel.create(start_time=10, end_time=20, image_file_id=2)

    sg1 = SuperchatSegmentItem.combine_segments(segment1, segment2)
    assert sg1.start_time == 0
    assert sg1.end_time == 20
    assert sg1.image_file_id == 1
