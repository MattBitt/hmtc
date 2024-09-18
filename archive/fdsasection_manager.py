from loguru import logger

from hmtc.models import Section, VideoModel


class SectionManager:
    def __init__(self, video, min_section_length=5):
        logger.error("💥💥💥💥💥💥DELETE ME (6/9/24) 💥💥💥💥💥💥")
        self.video = video
        self.sections = video.sections
        self.min_section_length = min_section_length

    @property
    def section_list(self):
        self.sections = (
            Section.select().join(VideoModel).where(Section.video_id == self.video.id)
        )
        return sorted(self.sections, key=lambda d: d.ordinal)

    def split_section_at(self, timestamp):
        try:
            timestamp = int(timestamp)
        except ValueError:
            logger.error(f"Invalid timestamp: {timestamp} for video {self.video.title}")
            return

        if timestamp < 0 or timestamp > self.video.duration:
            logger.error(f"Invalid timestamp: {timestamp} for video {self.video.title}")
            return

        sect = self.find_section(timestamp)
        if sect is None:
            logger.error(f"Could not find section for timestamp={timestamp}")
            return

        new_sect = Section.create(
            video=self.video,
            start=timestamp,
            end=sect.end,
            section_type=sect.section_type,
            is_first=False,
            is_last=sect.is_last,
            next_section=sect.next_section,
            ordinal=sect.ordinal + 1,
        )

        sect.is_last = False
        sect.next_section = new_sect
        sect.end = timestamp
        sect.save()

        logger.debug("Finshed adding section to video 🏠🏠🏠 ")

    def find_section(self, timestamp):
        # this is the section we want to split

        for sect in self.sections:
            if sect.start <= timestamp and sect.end >= timestamp:
                if (timestamp - sect.start) < self.min_section_length or (
                    sect.end - timestamp
                ) < self.min_section_length:
                    logger.error(
                        f"Section too short to split at timestamp={timestamp} for video {self.video.title}"
                    )
                    return None
                logger.debug(f"Found the correct section for timestamp={timestamp}")
                return sect
        return None

    def merge_sections(self, section1, section2):
        if section2 is None:
            logger.debug("Merging with last section")
            section2 = section1
            section1 = section1.previous_section

            logger.debug(f"Section1: {section1.get().ordinal}")
            logger.debug(f"Section2: {section2.get().ordinal}")
            return
        section1.end = section2.end
        section1.next_section = section2.next_section
        section1.is_last = section2.is_last
        section1.save()

        s = section2
        while s.next_section is not None:
            s = s.next_section
            s.ordinal -= 1
            s.save()

        section2.my_delete_instance()
        section2.save()
        logger.debug("Finished merging sections 🏠🏠🏠 ")

    def merge_section_with_next(self, ordinal):
        if len(self.section_list) == 1:
            logger.error("Not enough sections to merge")
            return

        sect = self.section_list[ordinal - 1]
        if sect is None:
            logger.error(f"Could not find section for ordinal={ordinal}")
            return

        self.merge_sections(sect, sect.next_section)
        logger.debug("Finished merging sections 🏠🏠🏠 ")
