from abc import ABC, abstractmethod
from custom_types import Vector
from enum import IntEnum


class SensorRange(IntEnum):
    PLUS_MINUS_25_MT = 1
    PLUS_MINUS_50_MT = 0
    PLUS_MINUS_100_MT = 2

    def to_float(self):
        return 25.0 if self.value == SensorRange.PLUS_MINUS_25_MT \
            else 50.0 if self.value == SensorRange.PLUS_MINUS_50_MT \
            else 100.0


class SensorCommunicationError(Exception):
    pass

class ISensorController(ABC):

    @abstractmethod
    def connect_and_init(self) -> bool:
        pass

    @abstractmethod
    def reconfigure(self, sensor_range: SensorRange) -> None:
        pass

    @abstractmethod
    async def read(self) -> Vector:
        pass

    @abstractmethod
    def start_stream(self) -> None:
        pass

    @abstractmethod
    def stop_stream(self) -> None:
        """ It is guaranteed that sensor will not stream more readings after this coroutine completes. """
        pass

    @abstractmethod
    def get_current_range(self) -> SensorRange:
        pass
