import ftd2xx as ftd
from serial import Serial
from serial.tools import list_ports
import time
import binascii
import sys
from constants import FTDI_PID, FTDI_VID
import struct

AVERAGES = 64
MESSAGE_TYPE_TEST = 0x00
MESSAGE_TYPE_RESET = 0x01
MESSAGE_TYPE_GET_READING = 0x02
MESSAGE_TYPE_START_STREAM = 0x03
MESSAGE_TYPE_STOP_STREAM = 0x04
MESSAGE_TYPE_READ_REGISTER = 0x05
MESSAGE_TYPE_SET_RANGE = 0x06

ports = list_ports.comports()
com_name = None
while True:
    for p in ports:
        if p.pid == FTDI_PID and p.vid == FTDI_VID:
            com_name = p.name

    if com_name:
        with Serial(com_name) as d:
            d.baudrate = 921600
            d.timeout = 0.5
            d.write_timeout = 0.5
            d.write(bytes([MESSAGE_TYPE_RESET, 0]))
            d.read(2)
            print("z - set 25 mT range, x - set 50 mT range, c - set 100 mT range, r - read, q - quit\r\n")

            while True:
                command = input()
                if command == "z":
                    d.write(bytes([MESSAGE_TYPE_SET_RANGE, 1]))
                    d.read(2)
                elif command == "x":
                    d.write(bytes([MESSAGE_TYPE_SET_RANGE, 0]))
                    d.read(2)
                elif command == "c":
                    d.write(bytes([MESSAGE_TYPE_SET_RANGE, 2]))
                    print(d.read(2))
                elif command == "r" or command == "":
                    x = 0.0
                    y = 0.0
                    z = 0.0
                    for i in range (AVERAGES):
                        d.write(bytes([MESSAGE_TYPE_GET_READING, 0]))
                        raw = d.read(14)
                        x += (1000 * float(*struct.unpack('>f', raw[2:6][::-1]))) / AVERAGES
                        y += (1000 * float(*struct.unpack('>f', raw[6:10][::-1]))) / AVERAGES
                        z += (1000 * float(*struct.unpack('>f', raw[10:14][::-1]))) / AVERAGES
                    # vals = [struct.unpack('>f', x), struct.unpack('>f', y),
                    #         struct.unpack('>f', z)]
                    print(f"x: {x:.3f} mT, y: {y:.3f} mT, z: {z:.3f} mT")
                elif command == "q":
                    sys.exit()



