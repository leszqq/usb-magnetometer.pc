from abc import ABC, abstractmethod
from custom_types import Vector, ReadingsChunk
from interfaces.i_sensor_controller import SensorRange


class IGuiController(ABC):

    @abstractmethod
    def update_measurement_text_field(self, measurements: ReadingsChunk) -> None:
        pass

    @abstractmethod
    def update_graph(self, measurements: ReadingsChunk) -> None:
        pass

    @abstractmethod
    def show_info(self, text: str, warning: bool = False) -> None:
        pass

    @abstractmethod
    def set_start_button_active(self, active: bool) -> None:
        pass

    @abstractmethod
    def set_stop_button_active(self, active: bool) -> None:
        pass

    @abstractmethod
    def set_range_buttons_active(self, active: bool) -> None:
        pass

    @abstractmethod
    def highlight_range_button(self, range: SensorRange) -> None:
        pass
