from hmtc.utils.mutagen_utils import read_id3_tags, write_id3_tags


def test_write_id3_tags(test_audio_filename):

    new_tag = {}
    new_tag["date"] = "2021"
    new_tag["artist"] = "Test Artist"
    new_tag["albumartist"] = ["Test Artist"]
    new_tag["album"] = "Test Album"
    new_tag["title"] = "Test Title"
    new_tag["tracknumber"] = "4"  # jellyfin doesn't work with mutli value tracknumber?
    new_tag["albumsort"] = "Test Album"
    new_tag["titlesort"] = "Test Title"

    id3 = write_id3_tags(file=test_audio_filename, tags=new_tag)
    mp3file = read_id3_tags(test_audio_filename)
    assert mp3file is not None
    assert mp3file["title"] == ["Test Title"]
    assert mp3file["artist"] == ["Test Artist"]
    assert mp3file["album"] == ["Test Album"]
    assert mp3file["date"] == ["2021"]
    assert mp3file["tracknumber"] == ["4"]
    assert mp3file["albumartist"] == ["Test Artist"]
    assert mp3file["albumsort"] == ["Test Album"]
    assert mp3file["titlesort"] == ["Test Title"]
