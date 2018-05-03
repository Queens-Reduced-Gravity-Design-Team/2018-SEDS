import logging
import serial
from serial.tools import list_ports
from threading import Lock
import struct


ControllerStates = [
    ("Do Nothing",     0),
    ("Emergency Stop", 1),
    ("Test LED ON",    2),
    ("Test LED OFF",   3)
]

ControllerMap = {}
for name, value in ControllerStates:
    ControllerMap[value] = name


class Controller:
    """
    Thread safe controller that communicates to the arduino
    """
    def __init__(self):
        self.currentPort = None
        self.IOLock = Lock()

    def getAvailablePorts(self):
        """
        Returns a list of available serial devices
        """
        ports = [port.device for port in list_ports.comports()]
        ports.append(None)

        return ports

    def close(self):
        self.IOLock.acquire()
        currentPort = self.currentPort
        if currentPort is not None:
            logging.debug("Closing serial port: {}".format(currentPort.name))
            currentPort.close()
            currentPort = None
        self.IOLock.release()

    def updatePort(self, newPort):
        """
        Updates or opens a new serial connection.
        """
        self.IOLock.acquire()
        if self.currentPort is not None:
            logging.debug(
                    "Closing serial port {}".format(self.currentPort.name))
            self.currentPort.close()

        if newPort is not None:
            self.currentPort = serial.Serial(newPort)
            logging.debug("Opened new port {}".format(newPort))
        self.IOLock.release()

    def listen(self, callback, Serial_ListenerEvent):
        logging.info("Begin listening to Serial")
        while Serial_ListenerEvent.is_set():
            self.IOLock.acquire()
            if self.currentPort is not None:
                line = self.currentPort.readline()
                callback(line)
            self.IOLock.release()

        logging.info("Recieved Serial_ListenerEvent close event.")
        Serial_ListenerEvent.set()

    def write(self, value):
        """
        Function used for writing a signal to the microcontroller. This can
        invoked manually, i.e. a button click, or by calling it in the code.

        For instance, this function may need to be called in handleNavpackets
        """
        if value not in ControllerMap:
            logging.error(
                    "Value {} is not specified by protocol".format(value))
            return

        name = ControllerMap[value]
        logging.info("Creating {} signal".format(name))

        # In an arduino, integers are 4 byte, little-enidian
        packedInteger = struct.pack("<i", value)
        logging.info("Sending bytes {}".format(packedInteger))

        self.IOLock.acquire()
        port = self.currentPort
        if port is not None:
            port.write(packedInteger)
        self.IOLock.release()

    def handleNavpackets(self, navPacket):
        """
        Sets the state of the serial outupt
        """
        return

    def handleSerialOutput(self, output):
        """
        Handles serial output.
        """
        return

