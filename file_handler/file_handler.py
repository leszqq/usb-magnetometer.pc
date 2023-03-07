from interfaces.i_file_explorer import IFileExplorer
from interfaces.i_file_saver import IFileSaver
from custom_types import MeasurementsChunk
from tkinter import filedialog, Tk
from pandas import read_csv, DataFrame
from datetime import datetime

from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go


_FILE_COLUMN_NAMES = ['t [s]', 'Bx [mT]', 'By [mT]', 'Bz [mT]']
_FILE_HEADER = ','.join(_FILE_COLUMN_NAMES)


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
            df.to_csv(f, index=False)

    @staticmethod
    def explore_file() -> None:

        def make_plot(df: DataFrame):
            fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
            fig.add_trace(go.Scattergl(x=df['t [s]'], y=df['Bx [mT]'], name='Bx [mT]'), row=1, col=1)
            fig.add_trace(go.Scattergl(x=df['t [s]'], y=df['By [mT]'], name='By [mT]'), row=1, col=1)
            fig.add_trace(go.Scattergl(x=df['t [s]'], y=df['Bz [mT]'], name='Bz [mT]'), row=1, col=1)
            fig.update_layout(title_text=f"{file.name}")
            fig.update_xaxes(title_text="Time [s]", row=1, col=1)
            fig.update_yaxes(title_text="Magnetic Flux Density B [mT]", row=1, col=1)
            _PLOT_CONFIG = dict({'scrollZoom': True})
            fig.show(config=_PLOT_CONFIG)
            pass
        try:
            file = filedialog.askopenfile(mode='r', filetypes=[("CSV Files", " .csv")])
            if not _FILE_HEADER == file.readline().rstrip('\n'):
                raise InvalidFileError
            file.seek(0)
            df = read_csv(file)
            make_plot(df)
        except InvalidFileError:
            raise InvalidFileError
