from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from Processor.action import Action


class Crop(Action):
    def __init__(self):
        super().__init__()

    def run(self):
        ffmpeg_extract_subclip(self.files[0].location,
                               self.params.slider_start,
                               self.params.slider_end,
                               targetname=self.destination)
