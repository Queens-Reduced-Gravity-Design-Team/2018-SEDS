import logging
import serial
from serial.tools import list_ports
from threading import Lock


ControllerStates = [
    ("Do Nothing",     0),
    ("Emergency Stop", 1),
    ("Test LED ON",    2),
    ("Test LED OFF",   3)
]


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
        currentPort = self.currentPort
        if currentPort is not None:
            logging.debug("Closing serial port: {}".format(currentPort.name))
            currentPort.close()
            currentPort = None

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

    def handleNavpackets(self, navPacket):
        """
        Sets the state of the serial outupt
        """
        return
