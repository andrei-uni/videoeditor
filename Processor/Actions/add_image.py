from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

from Processor.action import Action
from Processor.videoboundsforslider import VideoBoundsForSlider
from Processor.ineedimage import INeedImage


class AddImage(Action, VideoBoundsForSlider, INeedImage):
    def __init__(self):
        super().__init__()

    def run(self):
        at_seconds = self.params.extra_slider_value

        clip = self.files[0].clip
        first = clip.subclip(0, at_seconds)
        second = clip.subclip(at_seconds, clip.end)

        image = ImageClip(self.params.image_destination).set_duration(2)

        final = concatenate_videoclips([first, image, second], method='compose')
        final.write_videofile(self.destination, fps=24)
