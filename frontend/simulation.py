"""
UDP broadcaster that simulates flight data.

Author: Viraj Bangari
"""

import socket
import struct
import time
import os

import navpacket


def getSimulatedPacket(time, zData):
    """
    Creates a packed flight data struct.
    """
    GPS_Time = time
    INS_Mode = navpacket.INS_GOOD
    GPS_Mode = 3
    Roll = 22.0
    Pitch = -14.2
    True_Heading = 180
    Angular_Rate_X = 250.2
    Angular_Rate_Y = -240.2
    Angular_Rate_Z = 232.
    Latitude = -32
    Longitude = 10
    Altitude = 112.1
    Velocity_North = 32.1
    Velocity_East = 12.1
    Velocity_Down = 123.2
    Acceleration_X = 0
    Acceleration_Y = 10
    Acceleration_Z = zData

    binary = struct \
        .pack(navpacket.FMT_STRING,
              GPS_Time, INS_Mode,
              GPS_Mode, Roll, Pitch,
              True_Heading, Angular_Rate_X,
              Angular_Rate_Y, Angular_Rate_Z,
              Latitude, Longitude, Altitude,
              Velocity_North, Velocity_East,
              Velocity_Down, Acceleration_X,
              Acceleration_Y,
              Acceleration_Z)

    return binary


if __name__ == "__main__":
    SAMPLE_PERIOD = 0.01  # 1/100 Hz
    START_TIME = time.time()

    # Load the data from the sample file into memory
    dataPath = os.path.join("data", "Flight B (4).txt")
    accelerationZData = None
    with open(dataPath) as f:
        f.readline()  # Skip the header file
        accelerationZData = [float(line) for line in f]

    # Create socket object that will use UDP protocol
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Broadcast the UDP data
    azIndex = 0
    while True:
        packet = getSimulatedPacket(
                time.time() - START_TIME,
                accelerationZData[azIndex])
        sock.sendto(packet, (navpacket.HOST, navpacket.PORT))

        # Loop over flight data indefinately
        azIndex += 1
        if azIndex >= len(accelerationZData):
            azIndex = 0

        time.sleep(SAMPLE_PERIOD)
