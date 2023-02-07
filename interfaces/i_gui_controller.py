from abc import ABC, abstractmethod
from types import Vector
from typing import List


class IGuiController(ABC):

    @abstractmethod
    def update_measurement_text_fields(self, measurement: Vector):
        pass

    @abstractmethod
    def update_graph(self, measurements: List[Vector]):
        pass
