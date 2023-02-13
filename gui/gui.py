import asyncio
import typing

import numpy as np
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy_garden.graph import Graph, LinePlot
from scipy import signal

from custom_types import ReadingsChunk
from custom_types import Vector
from interfaces.i_gui_controller import IGuiController
from interfaces.i_gui_observer import IGuiObserver
from interfaces.i_gui_subject import IGuiSubject


# from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

class SplitBar(Widget):
    pass


class CustomButton(Button):
    _active = BooleanProperty(False)
    _highlighted = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        if self._active:
            self.background_color = self._highlighted_background_color

    def on_release(self):
        if self._highlighted:
            self.background_color = self._highlighted_background_color
        elif self._active:
            self.background_color = self._active_background_color


class CustomGraph(Graph):

    def __init__(self, **kwargs):
        super(CustomGraph, self).__init__(**kwargs)
        self._x_filt_state = None
        self._y_filt_state = None
        self._z_filt_state = None
        self._MAX_PLOT_POINTS = 1000
        self._data_fs = 20000
        self._time_range = 10.0
        self.xmax = self._time_range
        self.xmin = self.xmax - self._time_range
        self._data: ReadingsChunk = ReadingsChunk([], [], [], [])
        self._data_filtered: ReadingsChunk = ReadingsChunk([], [], [], [])
        self._data_decimated: ReadingsChunk = ReadingsChunk([], [], [], [])
        self._x_plot = LinePlot(color=[1, 0, 0, 1])
        self._y_plot = LinePlot(color=[0, 1, 0, 1])
        self._z_plot = LinePlot(color=[0, 0, 1, 1])
        self.add_plot(self._x_plot)
        self.add_plot(self._y_plot)
        self.add_plot(self._z_plot)
        self._update_aafilter()

    def _update_aafilter(self):
        _MIN_SIN_SAMPLES = 10
        self._aafilter = signal.iirfilter(N=8, Wn=(self._MAX_PLOT_POINTS / self._time_range) / _MIN_SIN_SAMPLES,
                                          btype='low', ftype='butter', output='sos', fs=self._data_fs)

        self._x_filt_state = np.zeros((self._aafilter.shape[0], 2))
        self._y_filt_state = np.zeros((self._aafilter.shape[0], 2))
        self._z_filt_state = np.zeros((self._aafilter.shape[0], 2))

    def update_data(self, chunk: ReadingsChunk, update_plot: bool = False):
        self._data.extend(chunk)

        filtered_chunk = ReadingsChunk(x=[], y=[], z=[], t=chunk.t)
        filtered_chunk.x, self._x_filt_state = signal.sosfilt(self._aafilter, chunk.x, zi=self._x_filt_state)
        filtered_chunk.y, self._y_filt_state = signal.sosfilt(self._aafilter, chunk.y, zi=self._y_filt_state)
        filtered_chunk.z, self._z_filt_state = signal.sosfilt(self._aafilter, chunk.z, zi=self._z_filt_state)
        self._data_filtered.extend(filtered_chunk)

        q = int(self._data_fs * self._time_range / self._MAX_PLOT_POINTS)
        decimated_chunk = ReadingsChunk([], [], [], [])
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

        self._x_plot.points = [(self._data_decimated.t[i], self._data_decimated.x[i]) for i in
                               range(s, len(self._data_decimated.t))]
        self._y_plot.points = [(self._data_decimated.t[i], self._data_decimated.y[i]) for i in
                               range(s, len(self._data_decimated.t))]
        self._z_plot.points = [(self._data_decimated.t[i], self._data_decimated.z[i]) for i in
                               range(s, len(self._data_decimated.t))]


class GuiLayout(BoxLayout):

    def __init__(self, **kwargs):
        super(GuiLayout, self).__init__(**kwargs)


class GuiApp(App):

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


class Gui(IGuiController, IGuiSubject):

    def __init__(self) -> None:
        self._gui_app = GuiApp()
        self._gui_task = asyncio.create_task(self._run())

        # self._test_readings = ReadingsChunk([], [], [], [])
        # asyncio.create_task(self.test())

    async def _run(self):
        await self._gui_app.async_run(async_lib='asyncio')

    async def wait_until_initialized(self) -> None:
        await self._gui_app.wait_until_started()

    def update_measurement_text_fields(self, measurement: Vector) -> None:
        pass

    # async def test(self):
    #     period = 0
    #     while True:
    #         SAMPLING_RATE = 20000
    #         UPDATE_PERIOD = 0.05
    #         SAMPLES_PER_UPDATE = int(SAMPLING_RATE * UPDATE_PERIOD)
    #         await asyncio.sleep(UPDATE_PERIOD)
    #         t = np.linspace((period * SAMPLES_PER_UPDATE) / SAMPLING_RATE,
    #                         ((1 + period) * SAMPLES_PER_UPDATE - 1) / SAMPLING_RATE,
    #                         SAMPLES_PER_UPDATE)
    #         period += 1
    #         x = 10 * np.sin(2 * np.pi * t) + 30 * np.random.rand(t.size) - 30 * np.random.rand(t.size)
    #         y = 20 * np.sin(2 * 4 * np.pi * t)
    #         z = 40 * np.sin(2 * 20 * np.pi * t)
    #         self._test_readings.t = t
    #         self._test_readings.x = x
    #         self._test_readings.y = y
    #         self._test_readings.z = z
    #
    #         self.update_graph(self._test_readings)

    def update_graph(self, measurements: ReadingsChunk) -> None:
        self._gui_app.root_layout.ids.graph.update_data(measurements)
        self._gui_app.root_layout.ids.graph.update_plot()

    def set_waiting_for_connection_message(self, shown: bool) -> None:
        pass

    def set_start_button(self, active: bool) -> None:
        pass

    def set_stop_button(self, active: bool) -> None:
        pass

    def attach_observer(self, observer: IGuiObserver) -> None:
        pass

    def set_preset_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.preset_selection_panel.value_string_prop = text

    def set_modulation_mode_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.modulation_mode_selection_panel.value_string_prop = text

    def set_modulation_mode_panel_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.modulation_mode_selection_panel.active_prop = active

    def set_squeeze_response_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.squeeze_response_selection_panel.value_string_prop = text

    def set_fixed_rate_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.fixed_rate_panel.value_string_prop = text

    def set_fixed_rate_panel_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.fixed_rate_panel.active_prop = active

    def set_minimum_rate_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.minimum_rate_panel.value_string_prop = text

    def set_minimum_rate_panel_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.minimum_rate_panel.active_prop = active

    def set_maximum_rate_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.maximum_rate_panel.value_string_prop = text

    def set_maximum_rate_panel_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.maximum_rate_panel.active_prop = active

    def set_squeeze_force_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.squeeze_force_panel.value_string_prop = text

    def set_next_preset_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.preset_selection_panel.ids.right_arrow.touch_callback = handler

    def set_previous_preset_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.preset_selection_panel.ids.left_arrow.touch_callback = handler

    def set_next_modulation_mode_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.modulation_mode_selection_panel.ids.right_arrow.touch_callback = handler

    def set_previous_modulation_mode_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.modulation_mode_selection_panel.ids.left_arrow.touch_callback = handler

    def set_next_squeeze_response_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.squeeze_response_selection_panel.ids.right_arrow.touch_callback = handler

    def set_previous_squeeze_response_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.squeeze_response_selection_panel.ids.left_arrow.touch_callback = handler

    def set_increase_fixed_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.fixed_rate_panel.ids.plus_sign.touch_callback = handler

    def set_decrease_fixed_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.fixed_rate_panel.ids.minus_sign.touch_callback = handler

    def set_increase_minimum_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.minimum_rate_panel.ids.plus_sign.touch_callback = handler

    def set_decrease_minimum_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.minimum_rate_panel.ids.minus_sign.touch_callback = handler

    def set_increase_maximum_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.maximum_rate_panel.ids.plus_sign.touch_callback = handler

    def set_decrease_maximum_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.maximum_rate_panel.ids.minus_sign.touch_callback = handler
