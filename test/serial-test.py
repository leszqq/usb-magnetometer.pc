import ftd2xx as ftd
from serial import Serial
from serial.tools import list_ports
import time
import binascii
import sys
from constants import FTDI_PID, FTDI_VID
import struct

MESSAGE_TYPE_TEST = 0x00
MESSAGE_TYPE_RESET = 0x01
MESSAGE_TYPE_GET_READING = 0x02
MESSAGE_TYPE_START_STREAM = 0x03
MESSAGE_TYPE_STOP_STREAM = 0x04
MESSAGE_TYPE_READ_REGISTER = 0x05
MESSAGE_TYPE_SET_RANGE = 0x06


def com_test():
    ports = list_ports.comports()
    com_name = None
    for p in ports:
        if p.pid == FTDI_PID and p.vid == FTDI_VID:
            com_name = p.name

    if com_name:
        with Serial(com_name) as d:
            d.baudrate = 921600
            d.timeout = 0.5
            d.write_timeout = 0.5

            print("Testing")
            d.write(bytes([MESSAGE_TYPE_TEST, 0]))
            response = d.read(2)
            print(f"got {binascii.hexlify(bytearray(response), ' ')}")

            print("initializing")
            d.write(bytes([MESSAGE_TYPE_RESET, 0]))
            response = d.read(2)
            print(f"got {binascii.hexlify(bytearray(response), ' ')}")

            print(f"reading registers")
            for i in range(20):
                d.write(bytes([MESSAGE_TYPE_READ_REGISTER, i]))
                response = d.read(4)
                print(f"{i} : {binascii.hexlify(bytearray(response), ' ')}")

            time.sleep(0.1)
            print(f"reading measurements")
            for i in range(5):
                d.write(bytes([MESSAGE_TYPE_GET_READING, 0]))
                response = d.read(14)
                print(f" {binascii.hexlify(bytearray(response), ' ')}")
                print(f"{struct.unpack('f', response[2:6])} {struct.unpack('f', response[6:10])} {struct.unpack('f', response[10:14])}")
    #with Serial('COM3') as ser:
        #ser.baudrate = 921600
        #sprint(ser)


def simple_test():
    d = ftd.open(0)
    try:
        d.setBaudRate(666666)
        d.setTimeouts(500, 500)

        print(d.getStatus())
        print(d.getDeviceInfo())

        print(f"testing")
        d.write(bytes([MESSAGE_TYPE_TEST, 0]))
        response = d.read(2)
        print(f"got {binascii.hexlify(bytearray(response), ' ')}")

        print("initializing")
        d.write(bytes([MESSAGE_TYPE_RESET, 0]))
        response = d.read(2)
        print(f"got {binascii.hexlify(bytearray(response), ' ')}")

        print(f"reading registers")
        for i in range(20):
            d.write(bytes([MESSAGE_TYPE_READ_REGISTER, i]))
            response = d.read(4)
            print(f"{i} : {binascii.hexlify(bytearray(response), ' ')}")

        time.sleep(0.1)
        print(f"reading measurements")
        for i in range(5):
            d.write(bytes([MESSAGE_TYPE_GET_READING, 0]))
            response = d.read(8)
            print(f" {binascii.hexlify(bytearray(response), ' ')}")
    except:
        print("Got exception")
    finally:
        d.close()
        sys.exit()


def disconnect_test():
    d = ftd.open(0)
    print(d)
    print(d.setBaudRate(666666))
    print(d.setTimeouts(500, 500))
    print(d.getStatus())
    print(d.getDeviceInfo())


def connected_test():
    devices = ftd.listDevices()
    if devices is None or len(devices) != 1:
        print("Device not connected or multiple devices connected")
    else:
        print("connected")


def stream_test():
    d = ftd.open(0)
    d.setBaudRate(921600)
    d.setTimeouts(200, 200)

    print(f"testing")
    d.write(bytes([MESSAGE_TYPE_TEST, 0]))
    response = d.read(2)
    print(f"got {binascii.hexlify(bytearray(response), ' ')}")

    print("initializing")
    d.write(bytes([MESSAGE_TYPE_RESET, 0]))
    response = d.read(2)
    print(f"got {binascii.hexlify(bytearray(response), ' ')}")
    #
    print(f"reading registers")
    for i in range(20):
        d.write(bytes([MESSAGE_TYPE_READ_REGISTER, i]))
        response = d.read(4)
        print(f"{i} : {binascii.hexlify(bytearray(response), ' ')}")

    time.sleep(0.1)
    print(f"reading measurements")
    for i in range(5):
        d.write(bytes([MESSAGE_TYPE_GET_READING, 0]))
        response = d.read(8)
        print(f" {binascii.hexlify(bytearray(response), ' ')}")

    time.sleep(0.1)
    print("Starting stream:")
    d.write(bytes([MESSAGE_TYPE_START_STREAM, 0]))
    response = d.read(2)
    print(f"got {binascii.hexlify(bytearray(response), ' ')}")
    chunk = d.read(CHUNK_PACKET_SIZE)
    print(f"got chunk: {chunk}")
    print(f"chunk size: {len(chunk)}")
    chunk = d.read(CHUNK_PACKET_SIZE)
    print(f"got chunk: {chunk}")
    print(f"chunk size: {len(chunk)}")
    d.write(bytes([MESSAGE_TYPE_STOP_STREAM, 0]))
    chunk = d.read(CHUNK_PACKET_SIZE)
    print(f"got chunk: {chunk}")
    print(f"chunk size: {len(chunk)}")
    d.write(bytes([MESSAGE_TYPE_SET_RANGE, 0]))
    response = d.read(2)
    print(f"got {binascii.hexlify(bytearray(response), ' ')}")


com_test()
