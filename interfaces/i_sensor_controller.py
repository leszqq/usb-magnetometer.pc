from abc import ABC, abstractmethod
from custom_types import Vector
from enum import Enum


class SensorRange(Enum):
    PLUS_MINUS_25_MT = 1
    PLUS_MINUS_50_MT = 2
    PLUS_MINUS_100_MT = 3


class ISensorController(ABC):

    @abstractmethod
    async def connect_and_init(self) -> None:
        pass

    @abstractmethod
    async def reconfigure(self, sensor_range: SensorRange) -> None:
        pass

    @abstractmethod
    async def read(self) -> Vector:
        pass

    @abstractmethod
    async def start_stream(self) -> None:
        pass

    @abstractmethod
    async def stop_stream(self) -> None:
        """ It is guaranteed that sensor will not stream more readings after this coroutine completes. """
        pass

    @abstractmethod
    def get_current_range(self) -> SensorRange:
        pass
