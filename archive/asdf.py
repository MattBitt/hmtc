def import_existing_tracks(filename):
    # these aren't really tracks.
    logger.error("This function is not implemented anymore...")
    return
    if not Path(filename).exists():
        logger.error(f"Track CSV not found {filename}")
    tracks = csv_to_dict(filename)
    for track in tracks:
        video = Video.get_or_none(Video.youtube_id == track["youtube_id"])

        if not video:
            # logger.error(f"Video not found to for this track {track}")
            continue
        if not video.sections:
            logger.error("Video has no initial section created in the DB.")
            continue

        if len(video.sections) > 1:
            logger.error(
                "New sections (after the initial) have already been created. Skipping import"
            )
            continue
        # for each 'track' insert a section break at the beginning
        # and at the end timestamps. mark the previous section
        # as talking, and the new section as music
        start_ts = int(track["start"])
        video.add_breakpoint(timestamp=start_ts)
        end_ts = int(track["end"])
        video.add_breakpoint(timestamp=end_ts)

        # using the ts +/- 5 below to not worry about edge cases
        # when the section is or isn't on the section break

        # section before the track
        prev_section_timestamp = start_ts - 5
        if prev_section_timestamp < 0:
            prev_section_timestamp = 0
        section = video.get_section_with_timestamp(timestamp=(prev_section_timestamp))
        section.section_type = "talking"
        section.save()

        # section containing the track
        section = video.get_section_with_timestamp(timestamp=(start_ts + 5))
        section.section_type = "music"
        section.save()

        # should also create a Track object with the words and stuff
        # but it shouldn't know anything about its position
        # within the Video (start/end)


def download_missing_files(self):
    download_path = WORKING / "downloads"
    media_path = STORAGE / "videos"

    thumbnail = self.poster is None
    subtitle = True
    info = True

    if not (thumbnail or subtitle or info):
        # logger.debug("All files already downloaded")
        return "", []

    video_info, files = download_video_info_from_id(
        self.youtube_id,
        download_path,
        thumbnail=thumbnail,
        subtitle=subtitle,
        info=info,
    )
    if video_info["error"] or files is None:
        logger.error(f"{video_info['error_info']}")
        return None, None
    else:
        new_path = Path(Path(media_path) / video_info["upload_date"][0:4])
        if not new_path.exists():
            new_path.mkdir(parents=True, exist_ok=True)

        # video_info["file_path"] = new_path
        return video_info, files
