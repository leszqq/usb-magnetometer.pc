from interfaces.i_gui_observer import IGuiObserver
from interfaces.i_gui_controller import IGuiController
from interfaces.i_measurement_consumer import IMeasurementConsumer
from interfaces.i_sensor_controller import ISensorController, SensorRange
from interfaces.i_sensor_controller import SensorCommunicationError
from custom_types import MeasurementsChunk
import asyncio
from enum import Enum
import logging
from file_handler.file_handler import FileHandler, InvalidFileError
from constants import FS
from typing import Optional

logger = logging.getLogger(__name__)

_MAX_FILE_TIME = 120


class AppState(Enum):
    SENSOR_DISCONNECTED = 1
    STANDBY = 2
    READING = 3
    TRANSITION = 4


class Supervisor(IGuiObserver, IMeasurementConsumer):
    def __init__(self, gui_controller: IGuiController, sensor_controller: ISensorController):
        self._gui = gui_controller
        self._sensor = sensor_controller
        self._measurements_queue = asyncio.Queue()
        self._measurements_buffer = MeasurementsChunk([], [], [], [])
        self._app_state = AppState.SENSOR_DISCONNECTED
        self._update_gui_buttons()
        self._reader_task: Optional[asyncio.Task] = None
        asyncio.create_task(self._connect_to_sensor())

    def on_start_button(self) -> None:
        if self._app_state == AppState.STANDBY:
            self._app_state = AppState.TRANSITION
            self._measurements_buffer = MeasurementsChunk([], [], [], [])
            self._gui.reset_graph()
            self._gui.reset_measurement_text_field()
            self._update_gui_buttons()
            self._reader_task = asyncio.create_task(self._read())

    def on_stop_button(self) -> None:
        if self._app_state == AppState.READING:
            self._app_state = AppState.TRANSITION
            self._update_gui_buttons()
            self._stop_reading()

    def on_25_mt_range_button(self) -> None:
        self._change_range_if_needed(SensorRange.PLUS_MINUS_25_MT)

    def on_50_mt_range_button(self) -> None:
        self._change_range_if_needed(SensorRange.PLUS_MINUS_50_MT)

    def on_100_mt_range_button(self) -> None:
        self._change_range_if_needed(SensorRange.PLUS_MINUS_100_MT)

    def on_explore_data_button(self) -> None:
        print("Starting plotly")
        try:
            FileHandler().explore_file()
        except InvalidFileError:
            self._gui.show_info('Invalid file selected',
                                warning=True)

    def on_save_data_button(self) -> None:
        print("Saving data to csv")
        FileHandler().save_to_file(self._measurements_buffer)

    def feed_measurements(self, measurements: MeasurementsChunk) -> None:
        if self._app_state == AppState.READING:
            self._measurements_queue.put_nowait(measurements)
            pass

    async def _connect_to_sensor(self):
        while True:
            try:
                self._sensor.connect_and_init()
                break
            except SensorCommunicationError:
                self._gui.show_info('Probe not connected, multiple probes connected or ftd2xx drivers not installed',
                                    warning=True)
                await asyncio.sleep(0.5)
        self._app_state = AppState.STANDBY
        self._update_gui_buttons()

    async def _read(self):

        async def get_from_queue(queue, content):
            chunk: MeasurementsChunk = await queue.get()
            content.extend(chunk)
        try:
            self._flush_measurements_queue()
            self._sensor.start_stream()
            self._app_state = AppState.READING
            self._update_gui_buttons()

            i = 0
            while True:
                measurements: Optional[MeasurementsChunk] = MeasurementsChunk([], [], [], [])
                await asyncio.wait_for(get_from_queue(self._measurements_queue, measurements), timeout=0.2)
                self._gui.update_measurement_text_field(measurements)
                self._gui.update_graph(measurements)
                self._measurements_buffer.extend(measurements)
                i += 1
                if i > 100:
                    i = 0
                    self._measurements_buffer.drop_older_than(int(FS * _MAX_FILE_TIME))
        except (SensorCommunicationError, asyncio.TimeoutError):
            if self._app_state == AppState.READING:
                self._app_state = AppState.SENSOR_DISCONNECTED
                await self._connect_to_sensor()

    def _stop_reading(self):
        self._sensor.stop_stream()
        self._reader_task.cancel()
        self._app_state = AppState.STANDBY
        self._update_gui_buttons()

    def _reconfigure(self, sensor_range: SensorRange):
        self._sensor.reconfigure(sensor_range)
        self._current_sensor_range = sensor_range
        self._app_state = AppState.STANDBY
        self._update_gui_buttons()

    def _change_range_if_needed(self, new_range: SensorRange):
        if self._app_state == AppState.STANDBY:
            if self._sensor.get_current_range() != new_range:
                self._app_state = AppState.TRANSITION
                self._update_gui_buttons()
                try:
                    self._reconfigure(new_range)
                except SensorCommunicationError:
                    self._app_state = AppState.SENSOR_DISCONNECTED
                    asyncio.create_task(self._connect_to_sensor())
                    return

    def _update_gui_buttons(self):

        def disable_all_buttons():
            self._gui.set_range_buttons_active(False)
            self._gui.set_start_button_active(False)
            self._gui.set_stop_button_active(False)
            self._gui.set_explore_data_button(False)
            self._gui.set_save_data_button(False)

        if self._app_state == AppState.TRANSITION:
            pass
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

        self._gui.highlight_range_button(self._sensor.get_current_range())

    def _flush_measurements_queue(self):
        while True:
            try:
                _ = self._measurements_queue.get_nowait()
            except asyncio.QueueEmpty:
                return
