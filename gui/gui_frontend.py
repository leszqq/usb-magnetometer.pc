import numpy as np
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivymd.app import MDApp
from kivymd.uix.behaviors import HoverBehavior
from kivy_garden.graph import Graph, LinePlot
from scipy import signal
from typing import Optional, Callable
from custom_types import MeasurementsChunk
import asyncio
from math import sqrt
from time import perf_counter
from constants import FS

class CustomButton(Button, HoverBehavior):
    active = BooleanProperty(False)
    highlighted = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._on_press_callback: Optional[Callable] = None

    def set_on_press_callback(self, callback: Callable):
        self._on_press_callback = callback

    def on_enter(self):
        if self.active and not self.highlighted:
            self.background_color = self._highlighted_background_color

    def on_leave(self):
        if self.active and not self.highlighted:
            self.background_color = self._active_background_color

    def on_press(self):
        if self.active:
            if self._on_press_callback and not self.highlighted:
                self._on_press_callback()

    def set_active(self, active: bool):
        self.active = active

    def set_highlighted(self, highlighted: bool):
        self.highlighted = highlighted


class InfoBar(Label):

    def __init__(self, **kwargs):
        super(InfoBar, self).__init__(**kwargs)

    def set_message(self, message: str, warning: bool = False):
        if message == '':
            self.text = ''
            self.height = 0
            return

        if warning:
            color = [0.9, 0, 0, 1]
        else:
            color = [1, 1, 1, 1]
        self.text = '    ' + message
        self.height = 30
        self.color = color


class FilteredMeasurements(BoxLayout):
    x_text = StringProperty('')
    y_text = StringProperty('')
    z_text = StringProperty('')
    m_text = StringProperty('')

    def __init__(self, **kwargs):
        super(FilteredMeasurements, self).__init__(**kwargs)
        self._next_update_time = 0.0
        self._x_filt_state = None
        self._y_filt_state = None
        self._z_filt_state = None
        self._update_filters()
        self.font_name = 'Cour'

    def update(self, chunk: MeasurementsChunk) -> None:
        x, self._x_filt_state = signal.sosfilt(self._aafilter, chunk.x, zi=self._x_filt_state)
        y, self._y_filt_state = signal.sosfilt(self._aafilter, chunk.y, zi=self._y_filt_state)
        z, self._z_filt_state = signal.sosfilt(self._aafilter, chunk.z, zi=self._z_filt_state)

        if chunk.t[-1] > self._next_update_time:
            self._next_update_time += 0.2
            m = np.sqrt(x[-1] ** 2 + y[-1] ** 2 + z[-1] ** 2)
            self.x_text = f"  Bx:{x[-1]:7.2f} mT"
            self.y_text = f"By:{y[-1]:7.2f} mT"
            self.z_text = f"Bz:{z[-1]:7.2f} mT"
            self.m_text = f"|B|:{m:7.2f} mT"


    def _update_filters(self):
        self._aafilter = signal.iirfilter(N=5, Wn=2,
                                          btype='low', ftype='butter', output='sos', fs=FS)

        self._x_filt_state = np.zeros((self._aafilter.shape[0], 2))
        self._y_filt_state = np.zeros((self._aafilter.shape[0], 2))
        self._z_filt_state = np.zeros((self._aafilter.shape[0], 2))


class CustomGraph(Graph):

    def __init__(self, **kwargs):
        super(CustomGraph, self).__init__(**kwargs)
        self._MAX_PLOT_POINTS = 1000
        self._time_range = 10.0

        self._x_filt_state: Optional = None
        self._y_filt_state: Optional = None
        self._z_filt_state: Optional = None
        self._show_x: bool = True
        self._show_y: bool = True
        self._show_z: bool = True
        self._show_abs: bool = False
        self._data: Optional[MeasurementsChunk] = None
        self._data_filtered: Optional[MeasurementsChunk] = None
        self._data_decimated: Optional[MeasurementsChunk] = None
        self._x_plot: Optional[LinePlot] = LinePlot(color=[1, 0, 0, 1])
        self._y_plot: Optional[LinePlot] = LinePlot(color=[0, 1, 0, 1])
        self._z_plot: Optional[LinePlot] = LinePlot(color=[0, 0, 1, 1])
        self.add_plot(self._x_plot)
        self.add_plot(self._y_plot)
        self.add_plot(self._z_plot)
        self.reset()

    def _update_aafilter(self):
        _MIN_SIN_SAMPLES = 2
        self._aafilter = signal.iirfilter(N=8, Wn=(self._MAX_PLOT_POINTS / self._time_range) / _MIN_SIN_SAMPLES,
                                          btype='low', ftype='butter', output='sos', fs=FS)

        self._x_filt_state = np.zeros((self._aafilter.shape[0], 2))
        self._y_filt_state = np.zeros((self._aafilter.shape[0], 2))
        self._z_filt_state = np.zeros((self._aafilter.shape[0], 2))

    def update_data(self, chunk: MeasurementsChunk):
        self._data.extend(chunk)

        filtered_chunk = MeasurementsChunk(x=[], y=[], z=[], t=chunk.t)
        filtered_chunk.x, self._x_filt_state = signal.sosfilt(self._aafilter, chunk.x, zi=self._x_filt_state)
        filtered_chunk.y, self._y_filt_state = signal.sosfilt(self._aafilter, chunk.y, zi=self._y_filt_state)
        filtered_chunk.z, self._z_filt_state = signal.sosfilt(self._aafilter, chunk.z, zi=self._z_filt_state)
        self._data_filtered.extend(filtered_chunk)

        q = int(FS * self._time_range / self._MAX_PLOT_POINTS)
        decimated_chunk = MeasurementsChunk([], [], [], [])
        decimated_chunk.t = [filtered_chunk.t[i] for i in range(0, len(filtered_chunk.t), q)]
        decimated_chunk.x = [filtered_chunk.x[i] for i in range(0, len(filtered_chunk.x), q)]
        decimated_chunk.y = [filtered_chunk.y[i] for i in range(0, len(filtered_chunk.y), q)]
        decimated_chunk.z = [filtered_chunk.z[i] for i in range(0, len(filtered_chunk.z), q)]
        self._data_decimated.extend(decimated_chunk)

    def update_plot(self):
        if self._data_decimated.t[-1] > self.xmax:
            self.xmax += self._time_range * 0.8
            self.xmin += self._time_range * 0.8

        s = next(x for x, val in enumerate(self._data_decimated.t) if val > self.xmin)

        try:
            if self._show_x:
                self._x_plot.points = [(self._data_decimated.t[i], self._data_decimated.x[i]) for i in
                                       range(s, len(self._data_decimated.t))]
            if self._show_y:
                self._y_plot.points = [(self._data_decimated.t[i], self._data_decimated.y[i]) for i in
                                       range(s, len(self._data_decimated.t))]
            if self._show_z:
                self._z_plot.points = [(self._data_decimated.t[i], self._data_decimated.z[i]) for i in
                                       range(s, len(self._data_decimated.t))]
        except IndexError:
            print("XD")
    def reset(self):
        self.xmax = self._time_range
        self.xmin = self.xmax - self._time_range
        self._data: MeasurementsChunk = MeasurementsChunk([], [], [], [])
        self._data_filtered: MeasurementsChunk = MeasurementsChunk([], [], [], [])
        self._data_decimated: MeasurementsChunk = MeasurementsChunk([], [], [], [])
        self._x_plot.points = []
        self._y_plot.points = []
        self._z_plot.points = []
        self._update_aafilter()


class GuiLayout(BoxLayout):

    def __init__(self, **kwargs):
        super(GuiLayout, self).__init__(**kwargs)


class GuifrontendApp(App):

    def __init__(self) -> None:
        super().__init__()
        Window.size = (800, 600)
        # Window.maximize()
        Window.minimum_width, Window.minimum_height = (800, 600)
        self._root_layout = None
        self._start_event = asyncio.Event()

    def build(self) -> GuiLayout:
        self._root_layout = GuiLayout()
        return self._root_layout

    def on_start(self):
        self._start_event.set()

    async def wait_until_started(self) -> None:
        await self._start_event.wait()

    @property
    def root_layout(self) -> GuiLayout:
        return self._root_layout
