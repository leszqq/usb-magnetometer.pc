from abc import ABC, abstractmethod
from interfaces.i_gui_observer import IGuiObserver


class IGuiSubject(ABC):

    @abstractmethod
    def attach_observer(self, observer: IGuiObserver) -> None:
        pass
