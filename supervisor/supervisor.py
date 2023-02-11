from interfaces.i_gui_observer import IGuiObserver
from interfaces.i_gui_controller import IGuiController
from interfaces.i_measurement_consumer import IMeasurementConsumer
from interfaces.i_sensor_controller import ISensorController, SensorRange
from custom_types import Vector
from typing import List
import asyncio
from enum import Enum
import logging

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
        self._reading_queue = asyncio.Queue() # TODO: set type of readings list

        self._app_state = AppState.SENSOR_DISCONNECTED
        asyncio.create_task(self._connect_to_sensor())

    def on_start_button(self) -> None:
        if self._app_state == AppState.STANDBY:
            self._app_state = AppState.TRANSITION
            asyncio.create_task(self._read())

    def on_stop_button(self) -> None:
        if self._app_state == AppState.READING:
            self._app_state = AppState.TRANSITION
            asyncio.create_task(self._stop_reading())
            pass

    def on_25_mt_range_button(self) -> None:
        self._change_range_if_needed(SensorRange.PLUS_MINUS_25_MT)

    def on_50_mt_range_button(self) -> None:
        self._change_range_if_needed(SensorRange.PLUS_MINUS_50_MT)

    def on_100_mt_range_button(self) -> None:
        self._change_range_if_needed(SensorRange.PLUS_MINUS_100_MT)

    def feed_measurement(self, measurement: Vector) -> None:
        if self._app_state == AppState.READING:
            # TODO: store measurement in queue
            pass

    def feed_measurements(self, measurements: List[Vector]) -> None:
        if self._app_state == AppState.READING:
            # TODO: store measurements in queue
            self._reading_queue.put_nowait(measurements)
            pass

    async def _connect_to_sensor(self):
        logger.info("supervisor: Connecting to sensor...")
        self._gui.set_waiting_for_connection_message(shown=True)
        await self._sensor.connect_and_init()
        logger.info("supervisor: Connected to sensor")
        self._gui.set_waiting_for_connection_message(shown=False)
        self._app_state = AppState.STANDBY

    async def _read(self):
        # TODO: flush queue ex. self._reading_queue.flush()
        await self._sensor.start_stream()
        self._app_state = AppState.READING

        while True:
            measurements_chunk: List[Vector] = await self._reading_queue.get()
            logging.info(f"_read: Got {measurements_chunk}")
            # TODO: dequeue readings, process them and pass to gui to plot
            # TODO: buffer reading, so it can be stored in CSV later

    async def _stop_reading(self):
        await self._sensor.stop_stream()
        self._app_state = AppState.STANDBY

    async def _reconfigure(self, previous_state: AppState, sensor_range: SensorRange):
        await self._sensor.stop_stream()
        await self._sensor.reconfigure(sensor_range)
        self._current_sensor_range = sensor_range
        if previous_state == AppState.READING:
            asyncio.create_task(self._read())
        else:
            self._app_state = AppState.STANDBY

    def _change_range_if_needed(self, new_range: SensorRange):
        if self._app_state == AppState.READING or self._app_state == AppState.STANDBY:
            if self._current_sensor_range != new_range:
                previous_app_state: AppState = self._app_state
                self._app_state = AppState.TRANSITION
                asyncio.create_task(self._reconfigure(previous_app_state, new_range))
