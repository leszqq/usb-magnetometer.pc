from abc import ABC, abstractmethod
from types import Vector

class ISensorController(ABC):

    @abstractmethod
    async def init(self) -> None:
        pass

    @abstractmethod
    async def reconfigure(self, sensor_config) -> None:
        pass

    @abstractmethod
    async def read(self) -> Vector:
        pass

    @abstractmethod
    async def start_streaming(self) -> None:
        pass

    @abstractmethod
    async def stop_streaming(self) -> None:
        pass
