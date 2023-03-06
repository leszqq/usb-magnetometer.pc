from abc import ABC, abstractmethod


class IFileExplorer(ABC):

    @staticmethod
    @abstractmethod
    def explore_file() -> None:
        pass
