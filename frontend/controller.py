import logging
import serial
from threading import Lock
import queue
import struct
from serial.tools import list_ports


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
        self.isAutomatic = False
        self.controllerEventQueue = queue.Queue()
        self.EVENT_LOOP_TIMEOUT = 1  # Seconds

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
        if self.currentPort is not None:
            logging.debug(
                    "Closing serial port {}".format(self.currentPort.name))
            self.currentPort.close()

        if newPort is not None:
            self.currentPort = serial.Serial(newPort)
            logging.debug("Opened new port {}".format(newPort))

    def listen(self, uiEventQueue, uiCallback, Serial_ListenerEvent):
        logging.info("Begin listening to Serial")
        while Serial_ListenerEvent.is_set():
            if self.currentPort is not None:
                data = self.unpackSerialOutput(self.currentPort.readline())
                uiEventQueue.put((data, uiCallback), block=False)
                self.controllerEventQueue.put((data, self.handleSerialOutput))

        logging.info("Recieved Serial_ListenerEvent close event.")
        Serial_ListenerEvent.set()

    def eventLoop(self, ControllerEventLoop_ListenerEvent):
        logging.info("Begin Serial Event loop")
        while ControllerEventLoop_ListenerEvent.is_set():
            try:
                data, callback = \
                    self.controllerEventQueue.get(
                        timeout=self.EVENT_LOOP_TIMEOUT)
                callback(data)
            except queue.Empty:
                continue

        logging.info("Recieved ControllerEventLoop close event.")
        ControllerEventLoop_ListenerEvent.set()

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

        port = self.currentPort
        if port is not None:
            port.write(packedInteger)

    def unpackSerialOutput(self, line):
        """ Unpacks the serial output recieved from the arduino """
        return struct.unpack("<i", line)

    def handleNavpackets(self, navPacket):
        """
        Sets the state of the serial outupt
        """
        if not self.isAutomatic:
            return

        # Just send a dummy "Do Nothing signal" when a navpacket is recieved.
        self.write(0)

        return

    def handleSerialOutput(self, output):
        """
        Handles serial output.
        """
        if not self.isAutomatic:
            return

        # Just send a dummy "Do Nothing signal" when a serial output is received.
        self.write(0)

        return
