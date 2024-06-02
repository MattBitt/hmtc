class old_SectionManager:
    def __init__(self, video):
        self.breakpoints = set([])
        self.video = video
        self.duration = video.duration

        for sect in video.sections:
            self.breakpoints.add(sect.start)
            self.breakpoints.add(sect.end)

    @classmethod
    def initialize(cls, video):
        return

    def create_initial_section(self):
        Section.create(
            start=0, end=self.duration, section_type="INITIAL", video=self.video
        )
        self.breakpoints = {0, self.duration}

    def add_breakpoint(self, timestamp):
        if timestamp in self.breakpoints:
            # logger.debug("Section Break already exists. Nothing to do")
            return
        old_section = self.find_section(timestamp=timestamp)
        Section.create(
            start=timestamp,
            end=old_section.end,
            section_type=old_section.section_type,
            video=self.video,
        )
        old_section.end = timestamp
        old_section.save()
        self.breakpoints.add(timestamp)

    def find_section(self, timestamp):
        for sect in self.all_sections:
            if (timestamp + 1) > sect.start and (timestamp - 1) < sect.end:
                return sect
        return None

    def find_both_sections(self, timestamp):
        for sect in self.all_sections:
            if sect.start == timestamp:
                after = sect
            if sect.end == timestamp:
                before = sect

        return before, after

    def delete_breakpoint(self, timestamp):
        if len(self.breakpoints) == 2:
            logger.error("No breakpoints to delete")
            return

        if timestamp not in self.breakpoints:
            logger.debug(f"Breakpoints: {self.breakpoints}")
            logger.error("Breakpoint doesn't exist")
            return

        before, after = self.find_both_sections(timestamp=timestamp)

        if before is None or after is None:
            logger.error("Couldn't find both sections")
            return

        before.end = after.end
        before.save()
        after.delete_instance()

    @property
    def all_sections(self):
        return sorted(self.video.sections, key=lambda x: x.start)

    @property
    def num_sections(self):
        return len(self.all_sections)

    @property
    def oldbreakpoints(self):
        breaks = set([])
        for sect in self.sections:
            breaks.add(sect.start)
            breaks.add(sect.end)
        return breaks
