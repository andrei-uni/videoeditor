from Processor.action import Action
from Processor.ineedextraslider import INeedExtraSlider

import moviepy.video.fx.all as vfx


class ChangeSpeed(Action, INeedExtraSlider):
    def __init__(self):
        super().__init__()

    def run(self):
        clip = self.files[0].clip
        final = clip.fx(vfx.speedx, self.params.extra_slider_value)
        final.write_videofile(self.destination)

    def extra_slider_start(self) -> float:
        return 0.1

    def extra_slider_end(self) -> float:
        return 10.0
