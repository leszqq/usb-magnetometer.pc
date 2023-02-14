import asyncio
from typing import Optional

from custom_types import Vector, MeasurementsChunk
from interfaces.i_sensor_controller import ISensorController, SensorRange
from interfaces.i_measurement_producer import IMeasurementProducer
from interfaces.i_measurement_consumer import IMeasurementConsumer
import logging
import asyncio
import math
import numpy as np


logger = logging.getLogger(__name__)


class SensorStub(ISensorController, IMeasurementProducer):

    def __init__(self):
        self._sensor_range = SensorRange.PLUS_MINUS_25_MT
        self._measurement_consumer: Optional[IMeasurementConsumer] = None

        self._reading_generator_task: Optional[asyncio.Task] = None

    async def connect_and_init(self) -> None:
        await asyncio.sleep(0.5)
        logger.info("sensor initialized")
        pass

    async def reconfigure(self, sensor_range: SensorRange) -> None:
        await asyncio.sleep(0.1)
        self._sensor_range = sensor_range
        logger.info("sensor reconfigured")
        pass

    async def read(self) -> Vector:
        pass

    async def start_stream(self) -> None:
        await asyncio.sleep(0.1)
        self._reading_generator_task = asyncio.create_task(self._generate_readings())
        pass

    async def stop_stream(self) -> None:
        """ It is guaranteed that sensor will not stream more readings after this coroutine completes. """
        logger.info("Stopping log stream")
        await asyncio.sleep(0.1)
        if self._reading_generator_task:
            self._reading_generator_task.cancel()

    def get_current_range(self) -> SensorRange:
        return self._sensor_range

    def attach_consumer(self, consumer: IMeasurementConsumer):
        self._measurement_consumer = consumer

    async def _generate_readings(self):
        UPDATE_PERIOD = 0.05
        SAMPLING_RATE = 20000
        SAMPLES_PER_UPDATE = int(SAMPLING_RATE * UPDATE_PERIOD)
        period = 0
        try:
            while True:
                await asyncio.sleep(UPDATE_PERIOD)
                if self._measurement_consumer:
                    t = np.linspace((period * SAMPLES_PER_UPDATE) / SAMPLING_RATE,
                                    ((1 + period) * SAMPLES_PER_UPDATE - 1) / SAMPLING_RATE,
                                    SAMPLES_PER_UPDATE)
                    period += 1
                    x = 20 + 30 * np.sin(2 * 0.333 * np.pi * t)  # + 30 * np.random.rand(t.size) - 30 * np.random.rand(t.size)
                    y = 20 * np.sin(2 * 1 * np.pi * t)  # + 30 * np.random.rand(t.size) - 30 * np.random.rand(t.size)
                    z = 10 * t
                    # z = 40 * np.sin(2 * 4 * np.pi * t)# + 30 * np.random.rand(t.size) - 30 * np.random.rand(t.size)
                    fake_measurements = MeasurementsChunk(t, x, y, z)
                    self._measurement_consumer.feed_measurements(fake_measurements)
        except:
            logger.info("_generate_readings cancelled")
