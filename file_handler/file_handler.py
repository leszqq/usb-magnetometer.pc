from interfaces.i_file_explorer import IFileExplorer
from interfaces.i_file_saver import IFileSaver
from custom_types import MeasurementsChunk
from tkinter import filedialog, Tk
from pandas import read_csv, DataFrame
from datetime import datetime

_FILE_COLUMN_NAMES = ['t [s]', 'Bx [mT]', 'By [mT]', 'Bz [mT]']
_FILE_HEADER = ''.join(_FILE_COLUMN_NAMES)


class InvalidFileError(Exception):
    pass


class FileHandler(IFileExplorer, IFileSaver):

    def __init__(self):
        Tk().withdraw()

    @staticmethod
    def save_to_file(measurements: MeasurementsChunk) -> None:
        f = filedialog.asksaveasfile(initialfile=datetime.now().strftime('%d-%m-%Y_%H_%M_%S.csv'),
                                     filetypes=[("CSV Files", " .csv")])
        if f:
            df = DataFrame(data={_FILE_COLUMN_NAMES[0]: measurements.t,
                                 _FILE_COLUMN_NAMES[1]: measurements.x,
                                 _FILE_COLUMN_NAMES[2]: measurements.y,
                                 _FILE_COLUMN_NAMES[3]: measurements.z})
            df.to_csv(f)

    @staticmethod
    def explore_file() -> None:
        try:
            file = filedialog.askopenfile(mode='r', filetypes=[("CSV Files", " .csv")])
            if not _FILE_HEADER == file.readline():
                raise InvalidFileError
            file.seek(0)
            df = read_csv(file)
        except InvalidFileError:
            raise InvalidFileError
