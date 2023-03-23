from abc import abstractmethod, ABCMeta


class INeedExtraSlider:
    __metaclass__ = ABCMeta

    @abstractmethod
    def extra_slider_start(self) -> float:
        """Provides a start value for extra slider"""

    @abstractmethod
    def extra_slider_end(self) -> float:
        """Provides an end value for extra slider"""
