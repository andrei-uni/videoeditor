from Processor.action import Action
from Processor.ineedextraslider import INeedExtraSlider


class Rotate(Action, INeedExtraSlider):
    def __init__(self):
        super().__init__()

    def run(self):
        clip = self.files[0].clip
        final = clip.add_mask().rotate(self.params.extra_slider_value)
        final.write_videofile(self.destination)

    def extra_slider_start(self) -> float:
        return 0

    def extra_slider_end(self) -> float:
        return 360
