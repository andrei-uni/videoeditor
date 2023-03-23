from threading import Thread
from abc import ABCMeta, abstractmethod

from Processor.params import Params
from file import File


class Action(Thread):
    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self):
        """Process files"""

    def set_fields(self, files: list[File], destination: str, params: Params):
        """Must be called before starting thread to set the fields needed for processing"""
        self.files = files
        self.destination = destination
        self.params = params
