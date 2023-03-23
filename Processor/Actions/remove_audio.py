from Processor.action import Action


class RemoveAudio(Action):
    def __init__(self):
        super().__init__()

    def run(self):
        clip = self.files[0].clip
        final = clip.without_audio()
        final.write_videofile(self.destination)
