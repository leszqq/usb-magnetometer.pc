from abc import ABC, abstractmethod
from custom_types import Vector, MeasurementsChunk
from typing import List


class IMeasurementConsumer(ABC):

    @abstractmethod
    def feed_measurements(self, measurements: MeasurementsChunk) -> None:
        pass
