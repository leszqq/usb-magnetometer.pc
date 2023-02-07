from abc import ABC, abstractmethod


class IGuiObserver(ABC):

    @abstractmethod
    def update_start_button_press(self):
        pass
