from abc import ABC, abstractmethod


class IGuiObserver(ABC):

    @abstractmethod
    def on_start_button(self) -> None:
        pass

    @abstractmethod
    def on_stop_button(self) -> None:
        pass

    @abstractmethod
    def on_25_mt_range_button(self) -> None:
        pass

    @abstractmethod
    def on_50_mt_range_button(self) -> None:
        pass

    @abstractmethod
    def on_100_mt_range_button(self) -> None:
        pass
