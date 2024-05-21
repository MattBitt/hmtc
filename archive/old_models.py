# def download_video(self):

#     download_path = WORKING / "downloads"
#     if self.has_video:
#         logger.debug(
#             "Video already downloaded. Delete it from the folder to redownload"
#         )
#         return
#     result, files = download_media_files(self.youtube_id, download_path)
#     if result:
#         for file in files:
#             self.add_file(file)

# def extract_audio(self):
#     if not self.has_video:
#         logger.error(f"No video file found for {self.title}")
#         return
#     logger.error("Need to redo query before this function will work again.")
#     return
#     # video_file = (
#     #     VideoFile.select(File)
#     #     .join(File)
#     #     .where((VideoFile.video_id == self.id) & (VideoFile.file_type == "video"))
#     # ).get()
#     path = Path(video_file.file.path)
#     vf = path / video_file.file.filename
#     af = path / f"{self.upload_date_str}___{self.youtube_id}.mp3"

#     command = f"ffmpeg -i {vf} -vn -acodec libmp3lame -y {af}"
#     logger.debug(f"Running command: {command}")
#     os.system(command)

#     self.add_file(af, file_type="audio")


# def update_episode_number(self, title, templates):
#     for template in templates:
#         match = re.search(template.template, title)
#         if match:
#             return match.group(1)

#         return ""


# @property
# def info(self):
#     logger.debug(f"Getting info file for playlist {self.title}")
#     i = (
#         File.select()
#         .where(File.file_type == "info")
#         .where(File.video == self)
#         .get_or_none()
#     )
#     # p = self.files.where(ChannelFile.file_type == "poster").get_or_none()
#     if i:
#         return i
#     return None

# @property
# def breakpoint_list(self):
#     return sorted([x.timestamp for x in self.breakpoints.select().distinct()])

# def add_breakpoint(self, timestamp):
#     if timestamp in self.breakpoint_list:
#         logger.debug("Section Break already exists. Nothing to do")
#         return
#     if timestamp > self.duration:
#         logger.error("Breakpoint can't be greater than duration")
#         return
#     Breakpoint.create(video=self, timestamp=timestamp)
#     logger.debug(f"Adding breakpoint to video {self.title}")

# def delete_breakpoint(self, timestamp):
#     if timestamp == 0 or timestamp == self.duration:
#         logger.error("Can't delete start or end breakpoints")
#         return

#     if timestamp not in self.breakpoint_list:
#         logger.debug(f"Breakpoints: {self.breakpoint_list}")
#         logger.error("Breakpoint doesn't exist")
#         return

#     bp = Breakpoint.get_or_none(
#         (Breakpoint.video == self) & (Breakpoint.timestamp == timestamp)
#     )
#     if bp is None:
#         logger.error("Couldn't find breakpoint")
#         return
#     bp.my_delete_instance()
#     self.breakpoints = Breakpoint.select().where(Breakpoint.video == self)

# def save(self, *args, **kwargs):
#     # if "manual" in kwargs:
#     #     self.manually_edited = kwargs["manual"]
#     # else:
#     #     self.manually_edited = False
#     # kwargs.pop("manual", None)
#     result = super(Video, self).save(*args, **kwargs)

#     # if self.num_sections == 0 and self.duration is not None:
#     #     Section.create_initial_section(video=self)
#     # if self.duration is not None and self.breakpoints.count() == 0:
#     #     logger.error(f"Duration is {self.duration}")
#     #     Breakpoint.create(video=self, timestamp=0)
#     #     Breakpoint.create(video=self, timestamp=self.duration)
#     return result
