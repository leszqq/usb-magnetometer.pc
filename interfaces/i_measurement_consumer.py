from abc import ABC, abstractmethod
from types import Vector
from typing import List


class IMeasurementConsumer(ABC):

    @abstractmethod
    def feed_measurement(self, measurement: Vector):
        pass

    @abstractmethod
    def feed_measurement_list(self, measurements: List[Vector]):
        pass
