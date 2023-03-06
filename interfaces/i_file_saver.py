from abc import ABC, abstractmethod
from custom_types import MeasurementsChunk


class IFileSaver(ABC):

    @staticmethod
    @abstractmethod
    def save_to_file(measurements: MeasurementsChunk) -> None:
        pass
