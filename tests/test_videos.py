from hmtc.schemas.video import VideoItem
from hmtc.models import Video as VideoModel


def test_xml_creator():
    new_vid = VideoModel.create(
        title="Test Video",
        description="This is a test video",
        youtube_id="123456",
        upload_date="2021-01-01",
        duration=1200,
    )

    VideoItem.create_xml_for_jellyfin(new_vid.id)
