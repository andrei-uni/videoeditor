from moviepy.video.compositing.concatenate import concatenate_videoclips
import moviepy.editor  # actually needed

from Processor.action import Action


class Concatenate(Action):
    def __init__(self):
        super().__init__()

    def run(self):
        clips = []
        for file in self.files:
            resized = file.clip.resize(width=self.files[0].clip.w)
            clips.append(resized)

        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(self.destination)
