import serial
from serial.tools import list_ports
import mttkinter.mtTkinter as tk
import logging
import threading
import sys

import navpacket


class App:
    def __init__(self, master, UDP_ListenerEvent):
        self.master = master
        master.title("Control Panel")

        # Thread syncronization objects
        self.UDP_ListenerEvent = UDP_ListenerEvent
        self.UDP_ListenerEvent.set()

        # Title
        self.label = tk.Label(master, text="Ugly Controller V1.0")

        # Serial port label
        self.label = tk.Label(master, text="Serial Port")
        self.label.grid(row=1, column=0)

        # Serial port dropdown
        self.currentPort = None
        self.serialPortVar = tk.StringVar()
        self.serialPortVar.set("")
        self.portSelector = \
            tk.OptionMenu(self.master, self.serialPortVar, "")
        self.portSelector.configure(width=18)
        self.portSelector.bind("<Button-1>", self.refreshPorts)
        self.portSelector.grid(row=1, column=1)

        # Selector for automatic mode
        self.isAutomatic = tk.BooleanVar()
        self.isAutomatic.set(False)
        self.checkButton = tk.Checkbutton(
            master, text="Automatic Mode", variable=self.isAutomatic,
            state=tk.NORMAL, onvalue=True, offvalue=False)
        self.checkButton.grid(row=2, column=0)

        # Label for milliseconds
        self.millisVar = tk.StringVar()
        self.millisVar.set(0)
        self.millis = tk.Label(self.master,
                               textvariable=self.millisVar,
                               font=('Courier', 15))
        self.millis.grid(row=3, column=0)

        # Label for z acceleration
        self.zAccelerationVar = tk.StringVar()
        self.zAccelerationVar.set(0)
        self.zAcceleration = tk.Label(self.master,
                                      textvariable=self.zAccelerationVar,
                                      font=('Courier', 15))
        self.zAcceleration.grid(row=3, column=1)

        # Determine cleanup protocol
        master.protocol("WM_DELETE_WINDOW", self.close)

    def getAvailablePorts(self):
        """
        Returns a list of available serial devices
        """
        ports = [port.device for port in list_ports.comports()]

        return ports

    def refreshPorts(self, event):
        """
        Refreshes list of serial devices in dropdown
        """
        logging.debug("Refreshing ports.")
        availablePorts = self.getAvailablePorts()

        # Delete old dropdown options
        self.portSelector["menu"].delete(0, "end")
        for value in availablePorts:
            self.portSelector["menu"] \
                .add_command(label=value,
                             command=lambda: self.updatePort(value))

        return

    def updatePort(self, value):
        """
        Update serial port to communicate with
        """
        currentPort = self.currentPort
        if currentPort is not None:
            logging.debug("Closing serial port {}".format(currentPort.name))
            currentPort.close()

        logging.debug("Opening new port {}".format(value))
        currentPort = serial.Serial(value)
        self.currentPort = currentPort
        self.serialPortVar.set(value)

    def close(self):
        """
        Cleans up, and then closes the application.
        """
        currentPort = self.currentPort
        logging.info("Closing connection")
        if currentPort is not None:
            logging.debug("Closing serial port {}".format(currentPort.name))
            currentPort.close()

        logging.info("Set event to close UDP_Listener")
        self.UDP_ListenerEvent.clear()

        self.master.destroy()

    def handleNavpacketsUI(self, navPacket):
        self.millisVar.set("{:.2f}".format(navPacket.GPS_Time))
        self.zAccelerationVar.set("{:.2f}".format(navPacket.Acceleration_Z))

    def handleNavpacketsControl(self, navPacket):
        return


if __name__ == "__main__":
    FMT = "%(levelname)s:%(threadName)s: %(message)s < %(module)s:%(lineno)s"
    logging.basicConfig(level=logging.DEBUG, format=FMT)

    # Create thread for UDP listener

    root = tk.Tk()

    UDP_ListenerEvent = threading.Event()
    app = App(root, UDP_ListenerEvent)
    t1 = threading.Thread(name="UDPThread",
                          target=navpacket.UDP_Listener,
                          args=(app.handleNavpacketsUI,
                                app.handleNavpacketsControl,
                                UDP_ListenerEvent))
    t1.start()
    root.mainloop()
    sys.exit()
