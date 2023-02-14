from interfaces.i_gui_observer import IGuiObserver
from interfaces.i_gui_controller import IGuiController
from interfaces.i_measurement_consumer import IMeasurementConsumer
from interfaces.i_sensor_controller import ISensorController, SensorRange
from custom_types import Vector, MeasurementsChunk
from typing import List
import asyncio
from enum import Enum
import logging
from time import perf_counter

logger = logging.getLogger(__name__)

class AppState(Enum):
    SENSOR_DISCONNECTED = 1
    STANDBY = 2
    READING = 3
    TRANSITION = 4


class Supervisor(IGuiObserver, IMeasurementConsumer):
    def __init__(self, gui_controller: IGuiController, sensor_controller: ISensorController):
        self._gui = gui_controller
        self._sensor = sensor_controller
        self._current_sensor_range = sensor_controller.get_current_range()
        self._measurements_queue = asyncio.Queue() # TODO: set type of readings list

        self._app_state = AppState.SENSOR_DISCONNECTED
        self._update_gui_buttons()
        asyncio.create_task(self._connect_to_sensor())

    def on_start_button(self) -> None:
        if self._app_state == AppState.STANDBY:
            self._app_state = AppState.TRANSITION
            self._gui.reset_graph()
            self._update_gui_buttons()
            asyncio.create_task(self._read())

    def on_stop_button(self) -> None:
        if self._app_state == AppState.READING:
            self._app_state = AppState.TRANSITION
            self._update_gui_buttons()
            asyncio.create_task(self._stop_reading())
            pass

    def on_25_mt_range_button(self) -> None:
        self._change_range_if_needed(SensorRange.PLUS_MINUS_25_MT)

    def on_50_mt_range_button(self) -> None:
        self._change_range_if_needed(SensorRange.PLUS_MINUS_50_MT)

    def on_100_mt_range_button(self) -> None:
        self._change_range_if_needed(SensorRange.PLUS_MINUS_100_MT)

    def on_explore_data_button(self) -> None:
        print("Starting plotly")

    def on_save_data_button(self) -> None:
        print("Saving data to csv")

    def feed_measurements(self, measurements: MeasurementsChunk) -> None:
        if self._app_state == AppState.READING:
            # TODO: store measurements in queue
            self._measurements_queue.put_nowait(measurements)
            pass


    async def _connect_to_sensor(self):
        await self._sensor.connect_and_init()
        self._app_state = AppState.STANDBY
        self._update_gui_buttons()

    async def _read(self):
        self._flush_measurements_queue()
        await self._sensor.start_stream()
        self._app_state = AppState.READING
        self._update_gui_buttons()

        while True:
            measurements: MeasurementsChunk = await self._measurements_queue.get()
            self._gui.update_measurement_text_field(measurements)
            self._gui.update_graph(measurements)
            # TODO: buffer reading, so it can be stored in CSV later

    async def _stop_reading(self):
        await self._sensor.stop_stream()
        self._app_state = AppState.STANDBY
        self._update_gui_buttons()

    async def _reconfigure(self, sensor_range: SensorRange):
        await self._sensor.reconfigure(sensor_range)
        self._current_sensor_range = sensor_range
        self._app_state = AppState.STANDBY
        self._update_gui_buttons()

    def _change_range_if_needed(self, new_range: SensorRange):
        if self._app_state == AppState.STANDBY:
            if self._current_sensor_range != new_range:
                self._app_state = AppState.TRANSITION
                self._update_gui_buttons()
                asyncio.create_task(self._reconfigure(new_range))

    def _update_gui_buttons(self):

        def disable_all_buttons():
            self._gui.set_range_buttons_active(False)
            self._gui.set_start_button_active(False)
            self._gui.set_stop_button_active(False)
            self._gui.set_explore_data_button(False)
            self._gui.set_save_data_button(False)

        if self._app_state == AppState.TRANSITION:
            pass
            # self._gui.show_info(' ')
            # disable_all_buttons()
        elif self._app_state == AppState.SENSOR_DISCONNECTED:
            self._gui.show_info("Waiting for sensor connected...", warning=True)
            disable_all_buttons()
        elif self._app_state == AppState.STANDBY:
            disable_all_buttons()
            self._gui.show_info("Standby")
            self._gui.set_start_button_active(True)
            self._gui.set_range_buttons_active(True)
            self._gui.set_explore_data_button(True)
            self._gui.set_save_data_button(True)
        elif self._app_state == AppState.READING:
            disable_all_buttons()
            self._gui.show_info("Reading")
            self._gui.set_stop_button_active(True)

        self._gui.highlight_range_button(self._current_sensor_range)

    def _flush_measurements_queue(self):
        while True:
            try:
                x = self._measurements_queue.get_nowait()
            except asyncio.QueueEmpty:
                return
