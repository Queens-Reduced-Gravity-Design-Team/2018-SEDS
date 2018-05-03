"""
UDP listener and flight data unpacker.

Author: Viraj Bangari
"""

import struct
from collections import namedtuple
import socket


# This is the format string for the expected from the data.
# Note: '>' implies Big Enidian
FMT_STRING = ">diiffffffdddffffff"


# Port to where expected data will arrive from
HOST = "localhost"
PORT = 5124


# INS_Modes
IMU_FAIL = 0
INS_SIM = 1
IMU_ONLY = 2
INS_ORIENTING = 3
INS_INITIALIZNG = 4
INS_DIVERGED = 5
INS_SOLNFREE = 6
INS_ALIGNING = 7
INS_HIGHVAR = 8
INS_GOOD = 9


def unpackNavPacket(data):
    NavPacket = namedtuple(
        "NavPacket",
        "GPS_Time " +
        "INS_Mode " +
        "GPS_Mode " +
        "Roll " +
        "Pitch " +
        "True_Heading " +
        "Angular_Rate_X " +
        "Angular_Rate_Y " +
        "Angular_Rate_Z " +
        "Latitude " +
        "Longitude " +
        "Altitude " +
        "Velocity_North " +
        "Velocity_East " +
        "Velocity_Down " +
        "Acceleration_X " +
        "Acceleration_Y " +
        "Acceleration_Z ")
    return NavPacket._make(struct.unpack(FMT_STRING, data))


if __name__ == "__main__":
    """
    Listens to UDP data and prints the corresponding NavPacket
    This code is blocking, so it should be run on a separate thread.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    bytesToRead = struct.calcsize(FMT_STRING)
    while True:
        data, address = sock.recvfrom(bytesToRead)
        navpacket = unpackNavPacket(data)

        print(navpacket.GPS_Time)
        print(navpacket.Acceleration_Z)
