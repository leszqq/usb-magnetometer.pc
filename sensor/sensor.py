import asyncio
import logging
from enum import IntEnum
from typing import Optional, Tuple
from serial import Serial
from constants import FTDI_PID, FTDI_VID
from serial.tools import list_ports
import ftd2xx as ftd
import numpy as np
from ftd2xx import DeviceError, FTD2XX, ftd2xx
from typing import List

from constants import FS
from custom_types import Vector, MeasurementsChunk
from interfaces.i_measurement_consumer import IMeasurementConsumer
from interfaces.i_measurement_producer import IMeasurementProducer
from interfaces.i_sensor_controller import ISensorController, SensorRange, SensorCommunicationError

_RESPONSE_SIZE = 2
_CHUNK_PACKET_SIZE = 480
_CHUNK_PERIOD = (_CHUNK_PACKET_SIZE / 6) / FS

_X_OFFSET_25_50 = 0.038
_Y_OFFSET_25_50 = 0.008
_Z_OFFSET_25_50 = -0.039

_X_OFFSET_100 = -0.188
_Y_OFFSET_100 = -0.180
_Z_OFFSET_100 = -0.179


class MessageType(IntEnum):
    TEST = 0
    RESET = 1
    GET_READING = 2
    START_STREAM = 3
    STOP_STREAM = 4
    READ_REGISTER = 5
    SET_RANGE = 6


class Request:

    def __init__(self, device, message_type: MessageType, data) -> None:
        self._bytes = bytes([message_type, data])
        self._device = device

    def send(self):
        try:
            self._device.write(self._bytes)
        except DeviceError:
            raise SensorCommunicationError


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

    def connect_and_init(self) -> None:

        ports = list_ports.comports()
        com_name = None
        for p in ports:
            if p.pid == FTDI_PID and p.vid == FTDI_VID:
                com_name = p.name

        if not com_name:
            raise SensorCommunicationError
        else:
            try:
                self._device = Serial(com_name)
                self._device.baudrate = 921600
                self._device.timeout = 1.0
                self._device.write_timeout = 1.0
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

    def reconfigure(self, sensor_range: SensorRange) -> None:
        Request(self._device, MessageType.SET_RANGE, int(sensor_range)).send()
        data = Response(self._device, MessageType.SET_RANGE).read()
        if data != bytes([0x00]):
            raise SensorCommunicationError
        self._sensor_range = sensor_range

    async def read(self) -> Vector:
        pass

    def start_stream(self) -> None:
        self._t0 = 0.0
        Request(self._device, MessageType.START_STREAM, 0).send()
        data = Response(self._device, MessageType.START_STREAM).read()
        if data != bytes([0x00]):
            raise SensorCommunicationError
        asyncio.create_task(asyncio.to_thread(self._stream_reader_task))

    def stop_stream(self) -> None:
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
            return 2.0 * (np.int16((data[1] << 8) | data[0]) / 2.0 ** 16) * self._sensor_range.to_float()

        while True:
            data: bytes = self._device.read(_CHUNK_PACKET_SIZE)
            if not any(data):
                break
            x: List[float] = [scale(bytes([msb, lsb])) for msb, lsb in zip(data[0::6], data[1::6])]
            y: List[float] = [scale(bytes([msb, lsb])) for msb, lsb in zip(data[2::6], data[3::6])]
            z: List[float] = [scale(bytes([msb, lsb])) for msb, lsb in zip(data[4::6], data[5::6])]
            t: List[float] = list((np.linspace(self._t0, self._t0 + _CHUNK_PERIOD, len(x), False, dtype=float)))

            if self._sensor_range == SensorRange.PLUS_MINUS_100_MT:
                x_off = _X_OFFSET_100
                y_off = _Y_OFFSET_100
                z_off = _Z_OFFSET_100
            else:
                x_off = _X_OFFSET_25_50
                y_off = _Y_OFFSET_25_50
                z_off = _Z_OFFSET_25_50

            x = [e - x_off for e in x]
            y = [e - y_off for e in y]
            z = [e - z_off for e in z]
            chunk = MeasurementsChunk(t, x, y, z)
            self._measurement_consumer.feed_measurements(chunk)
            self._t0 += _CHUNK_PERIOD

