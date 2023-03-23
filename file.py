from moviepy.video.io.VideoFileClip import VideoFileClip


class File:
    def __init__(self, location: str):
        self.location = location
        self.clip = VideoFileClip(location)
