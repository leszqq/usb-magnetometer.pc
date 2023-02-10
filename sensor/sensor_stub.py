import asyncio

from custom_types import Vector
from interfaces.i_sensor_controller import ISensorController, SensorRange
from interfaces.i_measurement_producer import IMeasurementProducer
from interfaces.i_measurement_consumer import IMeasurementConsumer
import logging

logger = logging.getLogger(__name__)

class Sensor(ISensorController, IMeasurementProducer):

    def __init__(self):
        self._sensor_range = SensorRange.PLUS_MINUS_25_MT

    async def connect_and_init(self) -> None:
        # STUB
        await asyncio.sleep(0.1)
        logger.info("sensor initialized")
        pass

    async def reconfigure(self, sensor_range: SensorRange) -> None:
        await asyncio.sleep(0.1)
        logger.info("sensor reconfigured")
        pass

    async def read(self) -> Vector:
        pass

    async def start_stream(self) -> None:
        pass

    async def stop_stream(self) -> None:
        """ It is guaranteed that sensor will not stream more readings after this coroutine completes. """
        pass

    def get_current_range(self) -> SensorRange:
        pass

    def attach_consumer(self, consumer: IMeasurementConsumer):
        pass

