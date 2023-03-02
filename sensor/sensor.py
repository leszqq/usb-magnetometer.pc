import asyncio
import logging
from enum import IntEnum
from typing import Optional, Tuple
from time import perf_counter
import ftd2xx as ftd
import numpy as np
from ftd2xx import DeviceError, FTD2XX
from typing import List

from constants import FS
from custom_types import Vector, MeasurementsChunk
from interfaces.i_measurement_consumer import IMeasurementConsumer
from interfaces.i_measurement_producer import IMeasurementProducer
from interfaces.i_sensor_controller import ISensorController, SensorRange, SensorCommunicationError

_RESPONSE_SIZE = 2
_CHUNK_PACKET_SIZE = 480
_CHUNK_PERIOD = (_CHUNK_PACKET_SIZE / 6) / FS


class MessageType(IntEnum):
    TEST = 0
    RESET = 1
    GET_READING = 2
    START_STREAM = 3
    STOP_STREAM = 4
    READ_REGISTER = 5


class Request:

    def __init__(self, device, message_type: MessageType, data) -> None:
        self._bytes = bytes([message_type, data])
        self._device = device

    def send(self):
        self._device.write(self._bytes)


class Response:

    def __init__(self, device, message_type: MessageType):
        self._message_type = message_type
        self._device = device

    def read(self) -> int:
        result: bytes = self._device.read(_RESPONSE_SIZE)
        message_type, data = self._decode(result)
        if message_type != self._message_type:
            raise SensorCommunicationError
        return data
        # TODO: add check if result ok

    @staticmethod
    def _decode(bytes_list: bytes) -> Tuple[MessageType, int]:
        return MessageType(bytes_list[0]), bytes_list[1:]


logger = logging.getLogger(__name__)


class Sensor(ISensorController, IMeasurementProducer):

    def __init__(self):
        self._sensor_range = SensorRange.PLUS_MINUS_50_MT
        self._measurement_consumer: Optional[IMeasurementConsumer] = None
        self._device: Optional[FTD2XX] = None
        self._connected = False
        self._t0 = 0.0
        self._reader_task: Optional = None
        self._stream_reading_done = True

    def connect_and_init(self) -> bool:

        devices = ftd.listDevices()
        if devices is None or len(devices) != 1:
            raise SensorCommunicationError
        try:
            self._device = ftd.open(0)
            self._device.setBaudRate(921600)
            self._device.setTimeouts(1000, 1000)
            Request(self._device, MessageType.TEST, 0).send()
            data = Response(self._device, MessageType.TEST).read()
            if data != bytes([0x00]):
                raise SensorCommunicationError
            Request(self._device, MessageType.RESET, 0).send()
            data = Response(self._device, MessageType.RESET).read()
            if data != bytes([0x00]):
                raise SensorCommunicationError
            self._connected = True
        except DeviceError:
            raise SensorCommunicationError

    async def reconfigure(self, sensor_range: SensorRange) -> None:
        pass

    async def read(self) -> Vector:
        pass

    def start_stream(self) -> None:
        self._t0 = 0.0
        Request(self._device, MessageType.START_STREAM, 0).send()
        data = Response(self._device, MessageType.START_STREAM).read()
        if data != bytes([0x00]):
            raise SensorCommunicationError
        asyncio.create_task(asyncio.to_thread(self._stream_reader_task))

    async def stop_stream(self) -> None:
        """ It is guaranteed that sensor will not stream more readings after this coroutine completes. """
        Request(self._device, MessageType.STOP_STREAM, 0).send()



    def get_current_range(self) -> SensorRange:
        return self._sensor_range

    def attach_consumer(self, consumer: IMeasurementConsumer):
        self._measurement_consumer = consumer

    def _exchange_messages(self, message_type: MessageType, data):
        pass

    @staticmethod
    def _exchanger_blocking_task():
        pass

    def _stream_reader_task(self):

        def scale(data: bytes):
            return (np.int16((data[0] << 8) | data[1]) / 2.0 ** 16) * self._sensor_range.to_float()

        i = 0
        while True:
            i += 1
            t0 = perf_counter()

            data: bytes = self._device.read(_CHUNK_PACKET_SIZE)
            print(f"chunk of size: {len(data)} read in {perf_counter() - t0}")
            # print(f"{data}")

            # if data[0] != MessageType.STREAM_CHUNK or data[1] != 0:
            #     raise SensorCommunicationError
            # t: List[float] = list(np.float_(np.arange(self._t0, self._t0 + _CHUNK_PERIOD, 1 / FS)))
            # self._t0 += _CHUNK_PERIOD
            # x: List[float] = [scale(bytes([msb, lsb])) for msb, lsb in zip(data[2::6], data[3::6])]
            # # y = np.zeros(1000)
            # # z = np.zeros(1000)
            # y: List[float] = [scale(bytes([msb, lsb])) for msb, lsb in zip(data[4::6], data[5::6])]
            # z: List[float] = [scale(bytes([msb, lsb])) for msb, lsb in zip(data[6::6], data[7::6])]


            self._t0 += _CHUNK_PERIOD
            if not any(data):
                print("Stopped")
                break
            x: List[float] = [scale(bytes([msb, lsb])) for msb, lsb in zip(data[0::6], data[1::6])]
            y: List[float] = [scale(bytes([msb, lsb])) for msb, lsb in zip(data[2::6], data[3::6])]
            z: List[float] = [scale(bytes([msb, lsb])) for msb, lsb in zip(data[4::6], data[5::6])]
            t: List[float] = list((np.linspace(self._t0, self._t0 + _CHUNK_PERIOD, len(x), False, dtype=float)))
            chunk = MeasurementsChunk(t, x, y, z)
            self._measurement_consumer.feed_measurements(chunk)
