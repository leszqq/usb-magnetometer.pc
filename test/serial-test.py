import ftd2xx
import ftd2xx as ftd
import pyftdi
import time
import binascii
import sys

MESSAGE_TYPE_TEST = 0x00
MESSAGE_TYPE_INIT_SENSOR = 0x01
MESSAGE_TYPE_GET_READING = 0x04
MESSAGE_TYPE_READ_REGISTER = 0x07

device_count = len(ftd.listDevices())
if device_count != 1:
    print("Device not connected or multiple devices connected")
    sys.exit()


def simple_test():
    d = ftd.open(0)
    try:
        d.setBaudRate(115200)
        d.setTimeouts(500, 500)

        print(d.getStatus())
        print(d.getDeviceInfo())

        print(f"testing")
        d.write(bytes([MESSAGE_TYPE_TEST, 0]))
        response = d.read(2)
        print(f"got {binascii.hexlify(bytearray(response), ' ')}")

        print("initializing")
        d.write(bytes([MESSAGE_TYPE_INIT_SENSOR, 0]))
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


simple_test()