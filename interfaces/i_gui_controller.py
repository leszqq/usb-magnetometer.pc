from abc import ABC, abstractmethod
from custom_types import Vector
from typing import List


class IGuiController(ABC):

    @abstractmethod
    def update_measurement_text_fields(self, measurement: Vector) -> None:
        pass

    @abstractmethod
    def update_graph(self, measurements: List[Vector]) -> None:
        pass

    @abstractmethod
    def set_waiting_for_connection_message(self, shown: bool) -> None:
        pass

    @abstractmethod
    def set_start_button(self, active: bool) -> None:
        pass

    @abstractmethod
    def set_stop_button(self, active: bool) -> None:
        pass
