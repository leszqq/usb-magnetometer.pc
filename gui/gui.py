import asyncio
import typing
from typing import Optional
import logging

import numpy as np

from gui.gui_frontend import GuifrontendApp
from custom_types import ReadingsChunk
from custom_types import Vector
from interfaces.i_gui_controller import IGuiController, SensorRange
from interfaces.i_gui_observer import IGuiObserver
from interfaces.i_gui_subject import IGuiSubject

logger = logging.getLogger(__name__)


class Gui(IGuiController, IGuiSubject):

    def __init__(self) -> None:
        self._gui_observer: Optional[IGuiObserver] = None
        self._gui_app = GuifrontendApp()
        self._gui_task = asyncio.create_task(self._run())

        self._test_readings = ReadingsChunk([], [], [], [])
        asyncio.create_task(self.test())

    async def _run(self):
        await self._gui_app.async_run(async_lib='asyncio')

    async def wait_until_initialized(self) -> None:
        await self._gui_app.wait_until_started()

    def update_measurement_text_field(self, measurements: ReadingsChunk) -> None:
        self._gui_app.root_layout.ids.filtered_measurements.update(measurements)

    async def test(self):
        period = 0
        while True:
            SAMPLING_RATE = 20000
            UPDATE_PERIOD = 0.05
            SAMPLES_PER_UPDATE = int(SAMPLING_RATE * UPDATE_PERIOD)
            await asyncio.sleep(UPDATE_PERIOD)
            t = np.linspace((period * SAMPLES_PER_UPDATE) / SAMPLING_RATE,
                            ((1 + period) * SAMPLES_PER_UPDATE - 1) / SAMPLING_RATE,
                            SAMPLES_PER_UPDATE)
            period += 1
            x = 20 + 30 * np.sin(2 * 0.333 * np.pi * t)  # + 30 * np.random.rand(t.size) - 30 * np.random.rand(t.size)
            y = 20 * np.sin(2 * 1 * np.pi * t)  # + 30 * np.random.rand(t.size) - 30 * np.random.rand(t.size)
            z = 10 * t
            # z = 40 * np.sin(2 * 4 * np.pi * t)# + 30 * np.random.rand(t.size) - 30 * np.random.rand(t.size)
            self._test_readings.t = t
            self._test_readings.x = x
            self._test_readings.y = y
            self._test_readings.z = z

            self.update_graph(self._test_readings)
            self.update_measurement_text_field(self._test_readings)

    def update_graph(self, measurements: ReadingsChunk) -> None:
        self._gui_app.root_layout.ids.graph.update_data(measurements)
        self._gui_app.root_layout.ids.graph.update_plot()

    def show_info(self, text: str, warning: bool = False):
        self._gui_app.root_layout.ids.info_bar.set_message(text, warning)

    def set_start_button_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.start_button.set_active(active)

    def set_stop_button_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.stop_button.set_active(active)

    def set_range_buttons_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.range_25_mt_button.set_active(active)
        self._gui_app.root_layout.ids.range_50_mt_button.set_active(active)
        self._gui_app.root_layout.ids.range_100_mt_button.set_active(active)

    def highlight_range_button(self, range: SensorRange) -> None:
        def unhiglight_all():
            self._gui_app.root_layout.ids.range_25_mt_button.set_highlighted(False)
            self._gui_app.root_layout.ids.range_50_mt_button.set_highlighted(False)
            self._gui_app.root_layout.ids.range_100_mt_button.set_highlighted(False)

        unhiglight_all()
        if range == SensorRange.PLUS_MINUS_25_MT:
            self._gui_app.root_layout.ids.range_25_mt_button.set_highlighted(True)
        elif range == SensorRange.PLUS_MINUS_50_MT:
            self._gui_app.root_layout.ids.range_50_mt_button.set_highlighted(True)
        elif range == SensorRange.PLUS_MINUS_100_MT:
            self._gui_app.root_layout.ids.range_100_mt_button.set_highlighted(True)

    def attach_observer(self, observer: IGuiObserver) -> None:
        self._gui_observer = observer
        gui_ids = self._gui_app.root_layout.ids
        gui_ids.start_button.set_on_press_callback(observer.on_start_button)
        gui_ids.stop_button.set_on_press_callback(observer.on_stop_button)
        gui_ids.range_25_mt_button.set_on_press_callback(observer.on_25_mt_range_button)
        gui_ids.range_50_mt_button.set_on_press_callback(observer.on_50_mt_range_button)
        gui_ids.range_100_mt_button.set_on_press_callback(observer.on_100_mt_range_button)

    def set_fixed_rate_panel_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.fixed_rate_panel.active_prop = active

    def set_minimum_rate_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.minimum_rate_panel.value_string_prop = text

    def set_next_preset_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.preset_selection_panel.ids.right_arrow.touch_callback = handler

    def set_previous_preset_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.preset_selection_panel.ids.left_arrow.touch_callback = handler
