from pathlib import Path
from typing import Any, Dict

from loguru import logger
from peewee import fn

from hmtc.config import init_config
from hmtc.db import init_db
from hmtc.domains.base_domain import BaseDomain
from hmtc.domains.video import Video
from hmtc.models import Disc as DiscModel
from hmtc.models import DiscFiles, db_null
from hmtc.models import DiscVideo as DiscVideoModel
from hmtc.models import Section as SectionModel
from hmtc.models import Track as TrackModel
from hmtc.models import Video as VideoModel
from hmtc.repos.disc_repo import DiscRepo
from hmtc.repos.file_repo import FileRepo
from hmtc.utils.ffmpeg_utils import extract_audio, extract_video
from hmtc.utils.general import clean_filename, my_copy_file, paginate
from hmtc.utils.lyric_utils import extract_lyrics
from hmtc.utils.mutagen_utils import write_id3_tags, write_mp4_metadata
from hmtc.utils.subtitles import extract_subs
from hmtc.utils.time_functions import ms_to_hms_and_ms, seconds_to_hms

config = init_config()
WORKING = Path(config["WORKING"])
STORAGE = Path(config["STORAGE"]) / "libraries"
db_instance = init_db(db_null, config)


class Disc(BaseDomain):
    model = DiscModel
    repo = DiscRepo()
    file_repo = FileRepo(DiscFiles)
    libraries = ["audio", "video"]

    def serialize(self) -> Dict[str, Any]:

        return {
            "id": self.instance.id,
            "title": self.instance.title,
            "folder_name": self.instance.folder_name,
            "order": self.instance.order,
            "album_title": self.instance.album.title,
            "num_videos": self.num_videos_on_disc(),
        }

    def folder(self, library):
        cleaned_title = clean_filename(self.instance.album.title)
        return (
            STORAGE
            / f"{library}/Harry Mack/{cleaned_title}/{self.instance.folder_name}"
        )

    def create_folders(self):
        cleaned_title = clean_filename(self.instance.album.title)
        for lib in self.libraries:
            folder = (
                STORAGE
                / f"{lib}/Harry Mack/{cleaned_title}/{self.instance.folder_name}"
            )
            folder.mkdir(exist_ok=True, parents=True)

    def num_videos_on_disc(self):
        return (
            DiscVideoModel.select(fn.COUNT(DiscVideoModel.id))
            .where(DiscVideoModel.disc_id == self.instance.id)
            .scalar()
        )

    def disc_number(self):
        return int(self.instance.folder_name[-3:])

    def add_file(self, file: Path, library: str):
        target_path = self.folder(library=library)

        # this is going to name everything as 'poster'
        # need to differentiate between filetypes at some
        # point.
        new_name = "poster"

        self.file_repo.add(
            item=self.instance, source=file, target_path=target_path, stem=new_name
        )

    def tracks(self):
        return TrackModel.select().where(TrackModel.disc_id == self.instance.id)

    def tracks_duration(self):
        return sum([x.length for x in self.tracks()])

    def videos(self):
        return (
            VideoModel.select()
            .join(DiscVideoModel, on=(VideoModel.id == DiscVideoModel.video_id))
            .where(DiscVideoModel.disc_id == self.instance.id)
            .order_by(DiscVideoModel.order.asc())
        )

    def video_duration(self):
        return sum([x.duration for x in self.videos()])

    def videos_paginated(self, current_page, per_page):
        disc_vids = (
            VideoModel.select()
            .join(DiscVideoModel, on=(VideoModel.id == DiscVideoModel.video_id))
            .where(
                VideoModel.id.in_(
                    DiscVideoModel.select(DiscVideoModel.video_id).where(
                        DiscVideoModel.disc_id == self.instance.id
                    )
                )
            )
            .order_by(DiscVideoModel.order.asc())
        )
        p = paginate(query=disc_vids, page=current_page.value, per_page=per_page)

        return p

    def swap_video_order(self, disc_vid_a: DiscVideoModel, disc_vid_b: DiscVideoModel):
        orig_a = disc_vid_a.order
        folder_a = disc_vid_a.disc.folder_name
        orig_b = disc_vid_b.order
        folder_b = disc_vid_b.disc.folder_name
        tmp_order = 999

        disc_vid_a.order = tmp_order
        disc_vid_a.save()
        disc_vid_b.order = orig_a
        disc_vid_b.save()
        disc_vid_b.disc.folder_name = folder_a
        disc_vid_b.disc.save()
        disc_vid_a.order = orig_b
        disc_vid_a.disc.folder_name = folder_b
        disc_vid_a.disc.save()
        disc_vid_a.save()

    def move_video_up(self, video: Video):
        disc_vid = (
            DiscVideoModel.select()
            .where(
                (DiscVideoModel.disc_id == self.instance.id)
                & (DiscVideoModel.video_id == video.instance.id)
            )
            .get()
        )
        target = (
            DiscVideoModel.select()
            .where(
                (DiscVideoModel.disc_id == self.instance.id)
                & (DiscVideoModel.order < disc_vid.order)
            )
            .order_by(DiscVideoModel.order.desc())
            .limit(1)
            .get_or_none()
        )
        if target is None:
            logger.error(f"Shouldn't be able to call this if theres no 'before' video")
            return

        logger.debug(f"swapping {disc_vid.order} and {target.order}")
        self.swap_video_order(disc_vid, target)

    def move_video_down(self, video: Video):
        disc_vid = (
            DiscVideoModel.select()
            .where(
                (DiscVideoModel.disc_id == self.instance.id)
                & (DiscVideoModel.video_id == video.instance.id)
            )
            .get()
        )
        target = (
            DiscVideoModel.select()
            .where(
                (DiscVideoModel.disc_id == self.instance.id)
                & (DiscVideoModel.order > disc_vid.order)
            )
            .order_by(DiscVideoModel.order.asc())
            .limit(1)
            .get_or_none()
        )
        if target is None:
            logger.error(f"Shouldn't be able to call this if theres no 'after' video")
            return

        logger.debug(f"swapping {disc_vid.order} and {target.order}")
        self.swap_video_order(disc_vid, target)

    def remove_video(self, video: Video):
        disc_vid = (
            DiscVideoModel.select()
            .where(
                (DiscVideoModel.disc_id == self.instance.id)
                & (DiscVideoModel.video_id == video.instance.id)
            )
            .get_or_none()
        )
        if disc_vid is None:
            logger.error(f"Disc Video not found.")
            return
        disc_vid.delete_instance()
        logger.success(f"Video {video} removed from Disc {self}")

    def num_tracks(self):
        num = (
            TrackModel.select(fn.COUNT(TrackModel.id))
            .where(TrackModel.disc_id == self.instance.id)
            .scalar()
        )
        if num is None:
            return 0
        return num

    def sections(self, fine_tuned=False):
        num_vids = self.num_videos_on_disc()
        if num_vids == 0:
            logger.debug(f"No videos found on this disc.")
            return 0

        if num_vids > 1:
            dvs = DiscVideoModel.select().where(
                DiscVideoModel.disc_id == self.instance.id
            )
            vid_ids = [v.video_id for v in dvs]
            query = SectionModel.select().where(SectionModel.video_id.in_(vid_ids))
        else:
            video = self.instance.dv.get()
            query = SectionModel.select().where(SectionModel.video_id == video.id)
        if fine_tuned:
            query = query.where(SectionModel.fine_tuned == True)

        return query

    def num_sections(self, fine_tuned=False):
        num_vids = self.num_videos_on_disc()
        if num_vids == 0:
            logger.debug(f"No videos found on this disc.")
            return 0

        if num_vids > 1:
            dvs = DiscVideoModel.select().where(
                DiscVideoModel.disc_id == self.instance.id
            )
            vid_ids = [v.video_id for v in dvs]
            query = SectionModel.select(fn.COUNT(SectionModel.id)).where(
                SectionModel.video_id.in_(vid_ids)
            )
        else:
            video = self.instance.dv.get().video
            query = SectionModel.select(fn.COUNT(SectionModel.id)).where(
                SectionModel.video_id == video.id
            )

        if fine_tuned:
            query = query.where(SectionModel.fine_tuned == True)

        num = query.scalar()

        if num is None:
            return 0

        return num

    def create_tracks(self):
        from hmtc.domains.section import Section
        from hmtc.domains.track import Track

        if self.num_tracks() > 0:
            logger.error(f"Delete the tracks first")
            return

        dvs = DiscVideoModel.select().where(DiscVideoModel.disc_id == self.instance.id)
        vid_ids = [x.video.id for x in dvs]
        vids = (
            VideoModel.select()
            .where(VideoModel.id.in_(vid_ids))
            .order_by(VideoModel.upload_date.asc())
        )
        track_number = 0

        for vid in vids:
            video = Video(vid.id)

            for section in video.sections():
                if not section.fine_tuned:
                    continue
                track_number += 1

                # 001 X-LARGE VS # 01
                track_number_padding = 3 if self.instance.xlarge else 2

                if track_number > 100 and not self.instance.xlarge:
                    logger.error(f"Too many tracks. This needs to be an X-large disc")
                    return None

                sect = Section(section)
                if sect.my_title() is None:
                    logger.error(f"No info found in section.")
                    return

                prefix = self.instance.album.prefix

                disc_number = str(int(self.instance.folder_name[-3:]))

                if prefix is not None:
                    if int(disc_number) == 0:
                        title = f"{prefix} X{str(track_number).zfill(track_number_padding)} {sect.my_title()}"
                    elif int(disc_number) >= 100:
                        title = f"{prefix}{disc_number}.{str(track_number).zfill(track_number_padding)} {sect.my_title()}"
                    else:
                        title = f"{prefix} {disc_number.zfill(2)}.{str(track_number).zfill(track_number_padding)} {sect.my_title()}"

                else:
                    title = f"{sect.my_title()}"

                mp4_file_path = Path(self.folder("video")) / f"{title}.mp4"
                if mp4_file_path.exists():
                    logger.error(f"{mp4_file_path} already exists. Quitting")
                    return
                mp4_file_path.parent.mkdir(exist_ok=True, parents=True)

                mp3_file_path = Path(self.folder("audio")) / f"{title}.mp3"
                if mp3_file_path.exists():
                    logger.error(f"{mp3_file_path} already exists. Quitting")
                    return
                mp3_file_path.parent.mkdir(exist_ok=True, parents=True)

                input_file = Path(video.file_repo.get(video.instance.id, "video").path)
                if not input_file.exists():
                    logger.error(f"{input_file} already exists. Quitting")
                    return

                extract_video(
                    input=input_file,
                    output=mp4_file_path,
                    start_time=ms_to_hms_and_ms(sect.instance.start),
                    end_time=ms_to_hms_and_ms(sect.instance.end),
                )
                extract_audio(
                    input=input_file,
                    output=mp3_file_path,
                    start_time=ms_to_hms_and_ms(sect.instance.start),
                    end_time=ms_to_hms_and_ms(sect.instance.end),
                )

                new_track = Track.create_from_section(sect, track_number, self, title)

                # seems like the jellyfin libraries work best with
                # id3 tags for audio and a title.nfo file for video

                poster = Path(self.poster_file().path)
                write_id3_tags(mp3_file_path, new_track.id3_dict(), poster)

                nfo = new_track.create_nfo(mp4_file_path.parent)

                new_track.file_repo.add(
                    item=new_track.instance,
                    source=nfo,
                    target_path=nfo.parent,
                    stem=nfo.name,
                )
                # add video file to db
                new_track.file_repo.add(
                    item=new_track.instance,
                    source=mp4_file_path,
                    target_path=mp4_file_path.parent,
                    stem=mp4_file_path.name,
                )
                # add audio file to db
                new_track.file_repo.add(
                    item=new_track.instance,
                    source=mp3_file_path,
                    target_path=mp3_file_path.parent,
                    stem=mp3_file_path.name,
                )

                # if i have subtitles, i should create them for the tracks as well
                # jellyfin seems to want .srt files for the music video
                # and .lrc for the audio (haven't seen autoscroll work yet)

                subtitle_file_path = Path(self.folder("video")) / f"{title}.srt"
                if subtitle_file_path.exists():
                    logger.error(f"{subtitle_file_path} already exists. Quitting")
                    return
                subtitle_file_path.parent.mkdir(exist_ok=True, parents=True)

                lyrics_file_path = Path(self.folder("audio")) / f"{title}.lrc"
                if lyrics_file_path.exists():
                    logger.error(f"{lyrics_file_path} already exists. Quitting")
                    return
                lyrics_file_path.parent.mkdir(exist_ok=True, parents=True)

                subtitle_input = video.file_repo.get(video.instance.id, "subtitle")
                if subtitle_input is not None:
                    subtitle_input_file = Path(subtitle_input.path)
                    if not subtitle_input_file.exists():
                        logger.error(f"{subtitle_input_file} already exists. Quitting")
                        return

                    extract_subs(
                        input=subtitle_input_file,
                        output=subtitle_file_path,
                        start_time=sect.instance.start // 1000,
                        end_time=sect.instance.end // 1000,
                    )
                    extract_lyrics(
                        input=subtitle_input_file,
                        output=lyrics_file_path,
                        start_time=ms_to_hms_and_ms(sect.instance.start),
                        end_time=ms_to_hms_and_ms(sect.instance.end),
                    )

                    # add subtitle file to db
                    new_track.file_repo.add(
                        item=new_track.instance,
                        source=subtitle_file_path,
                        target_path=subtitle_file_path.parent,
                        stem=subtitle_file_path.name,
                    )

                    # add lyrics file to db
                    new_track.file_repo.add(
                        item=new_track.instance,
                        source=lyrics_file_path,
                        target_path=lyrics_file_path.parent,
                        stem=lyrics_file_path.name,
                    )

            logger.success(f"Finished creating {track_number} tracks")

    def remove_tracks(self):
        from hmtc.domains.track import Track

        logger.debug(f"Disc {self} is about to remove its {self.num_tracks()} tracks.")
        for track in self.tracks():
            t = Track(track.id)
            t.delete()

    def use_poster_from_video(self, video: Video):
        # need to update the image in both libraries (i think)
        existing_poster = self.file_repo.get(self.instance.id, "poster")
        if existing_poster is not None:
            self.file_repo.delete(self.instance.id, "poster")

        poster = video.file_repo.get(video.instance.id, "poster")
        if poster is None:
            logger.error(f"No Poster found for {video}")
            return
        # copy the poster to the working directory, then add it to the disc item
        path = Path(poster.path)
        target = WORKING / path.name
        my_copy_file(path, target)
        self.add_file(target, "video")
