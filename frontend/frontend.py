import mttkinter.mtTkinter as tkinter
from tkinter import ttk as tk

import serial
from serial.tools import list_ports

import logging
import threading
import sys

import navpacket


class App:
    def __init__(self, master, UDP_ListenerEvent):
        self.master = master
        master.title("Control Panel")

        self.mainframe = tk.Frame(self.master, padding=(6, 6, 12, 12))
        self.mainframe.grid(sticky='nwse')

        # Thread syncronization objects
        self.UDP_ListenerEvent = UDP_ListenerEvent
        self.UDP_ListenerEvent.set()

        # Title
        self.title = tk.Label(self.mainframe,
                              text="Ugly Controller V1.0",
                              font=("TkDefaultFont", 20))
        self.title.grid(row=0, column=0, columnspan=2)

        # Serial port label
        self.label = tk.Label(self.mainframe, text="Serial Port")
        self.label.grid(row=1, column=0)

        # Serial port dropdown
        self.availablePorts = []
        self.currentPort = None
        self.serialPortVar = tkinter.StringVar()
        self.serialPortVar.set(None)
        self.portSelector = \
            tk.OptionMenu(self.mainframe, self.serialPortVar, "")
        self.portSelector.configure(width=18)
        self.portSelector.bind("<Button-1>", self.refreshPorts)
        self.portSelector.grid(row=1, column=1)

        # Selector for automatic mode
        self.isAutomatic = tkinter.BooleanVar()
        self.isAutomatic.set(False)
        self.checkButton = tk.Checkbutton(
            self.mainframe, text="Automatic Mode", variable=self.isAutomatic,
            state=tkinter.NORMAL, onvalue=True, offvalue=False)
        self.checkButton.grid(row=2, column=0)

        self.liveData = tk.Labelframe(self.mainframe, text="Live Data")
        self.liveData.grid(row=3, columnspan=3)

        # Label for milliseconds
        self.millisVar = tkinter.StringVar()
        self.millisVar.set(0)
        self.millis = tk.Label(self.liveData,
                               textvariable=self.millisVar,
                               font=('Courier', 13))
        self.millis.grid(in_=self.liveData, row=4, columnspan=3, sticky='w')

        # Label for z acceleration
        self.zAccelerationVar = tkinter.StringVar()
        self.zAccelerationVar.set(0)
        self.zAcceleration = tk.Label(self.liveData,
                                      textvariable=self.zAccelerationVar,
                                      font=('Courier', 13))
        self.zAcceleration.grid(
                in_=self.liveData, row=5, columnspan=3, sticky='w')

        # Determine cleanup protocol
        master.protocol("WM_DELETE_WINDOW", self.close)

    def getAvailablePorts(self):
        """
        Returns a list of available serial devices
        """
        ports = [port.device for port in list_ports.comports()]
        ports.append(None)

        return ports

    def refreshPorts(self, event):
        """
        Refreshes list of serial devices in dropdown
        """
        logging.debug("Refreshing ports.")
        self.availablePorts = self.getAvailablePorts()

        # Delete old dropdown options
        self.portSelector["menu"].delete(0, "end")
        for value in self.availablePorts:

            def _callback(value=value):
                self.updatePort(value)

            self.portSelector["menu"] \
                .add_command(label=value,
                             command=_callback)

        return

    def updatePort(self, value):
        """
        Update serial port to communicate with
        """
        currentPort = self.currentPort
        if currentPort is not None:
            logging.debug("Closing serial port {}".format(currentPort.name))
            currentPort.close()

        if value is not None:
            logging.debug("Opening new port {}".format(value))
            currentPort = serial.Serial(value)

        self.currentPort = currentPort
        self.serialPortVar.set(value)

    def close(self):
        """
        Cleans up, and then closes the application.
        """
        currentPort = self.currentPort
        if currentPort is not None:
            logging.debug("Closing serial port: {}".format(currentPort.name))
            currentPort.close()

        logging.info("Set event to close UDP_Listener")
        self.UDP_ListenerEvent.clear()

        self.master.destroy()

    def handleNavpacketsUI(self, navPacket):
        self.millisVar.set("t: {:.2f}s".format(navPacket.GPS_Time))
        self.zAccelerationVar.set(
                "az: {:.2f}m/s^2".format(navPacket.Acceleration_Z))

    def handleNavpacketsControl(self, navPacket):
        return


if __name__ == "__main__":
    FMT = "%(levelname)s:%(threadName)s: %(message)s < %(module)s:%(lineno)s"
    logging.basicConfig(level=logging.DEBUG, format=FMT)

    # Define thread events
    UDP_ListenerEvent = threading.Event()

    # Set up UI
    root = tkinter.Tk()
    root.resizable(width=False, height=False)
    app = App(root, UDP_ListenerEvent)

    # Create thread for UDP listener
    t1 = threading.Thread(name="UDPThread",
                          target=navpacket.UDP_Listener,
                          args=(app.handleNavpacketsUI,
                                app.handleNavpacketsControl,
                                UDP_ListenerEvent))
    try:
        t1.start()
        root.mainloop()
    except KeyboardInterrupt:
        app.close()
