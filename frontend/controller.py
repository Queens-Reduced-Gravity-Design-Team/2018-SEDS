import logging
import serial
from serial.tools import list_ports
from threading import Lock


class ControllerStates:
    DO_NOTHING = 0
    EMERGENCY_STOP = 1
    TEST_LED_ON = 2
    TEST_LED_OFF = 3


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
            logging.debug("Opening new port {}".format(newPort))
            self.currentPort = serial.Serial(newPort)

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
