from abc import ABC, abstractmethod
from custom_types import Vector
from typing import List


class IMeasurementConsumer(ABC):

    @abstractmethod
    def feed_measurement(self, measurement: Vector) -> None:
        pass

    @abstractmethod
    def feed_measurements(self, measurements: List[Vector]) -> None:
        pass
