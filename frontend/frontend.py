import tkinter
from tkinter import ttk as tk

import time
import logging
import threading

import navpacket as nav
import controller as cnt


class App:
    def __init__(
            self, master, UDP_ListenerEvent, Serial_ListenerEvent, controller):
        self.master = master
        master.title("Control Panel")
        self.controller = controller

        self.mainframe = tk.Frame(self.master, padding=(6, 6, 12, 12))
        self.mainframe.grid(sticky='nwse')

        # Thread syncronization objects
        self.UDP_ListenerEvent = UDP_ListenerEvent
        self.UDP_ListenerEvent.set()

        self.Serial_ListenerEvent = Serial_ListenerEvent
        self.Serial_ListenerEvent.set()

        # Title
        title = tk.Label(self.mainframe,
                         text="Ugly Controller V1.0",
                         font=("TkDefaultFont", 20))
        title.grid(row=0, column=0, columnspan=2)

        # Serial port label
        label = tk.Label(self.mainframe, text="Serial Port")
        label.grid(row=1, column=0)

        # Serial port dropdown
        self.availablePorts = []
        self.serialPortVar = tkinter.StringVar()
        self.serialPortVar.set(None)
        self.portSelector = \
            tk.OptionMenu(self.mainframe, self.serialPortVar, "")
        self.portSelector.configure(width=18)
        self.portSelector.bind("<Button-1>", self.refreshPorts)
        self.portSelector.grid(row=1, column=1)

        # Selector for automatic mode
        self.isAutomaticVar = tkinter.BooleanVar()
        self.isAutomaticVar.set(False)
        self.isAutomatic = self.isAutomaticVar.get()
        self.checkButton = tk.Checkbutton(
            self.mainframe,
            text="Automatic Mode",
            variable=self.isAutomaticVar,
            state=tkinter.ACTIVE,
            onvalue=True,
            offvalue=False,
            command=self.toggleAutomatic)
        self.checkButton.grid(row=2, column=0)

        # === Live data ===
        # Refresh options for live data labels
        self.navPacketRefreshPeriod = 0.3
        self.last_navRefresh = time.time()
        self.serialOutputRefreshPeriod = 0.3
        self.last_navRefresh = time.time()

        # Live data frame.
        self.liveData = tk.Labelframe(self.mainframe, text="Live Data")
        self.liveData.grid(row=3, columnspan=3)

        # Label for milliseconds
        self.millis = tk.Label(self.liveData,
                               text="0",
                               font=('Courier', 13))
        self.millis.grid(in_=self.liveData, row=4, columnspan=3, sticky='w')

        # Label for z acceleration
        self.zAcceleration = tk.Label(self.liveData,
                                      text="0",
                                      font=('Courier', 13))
        self.zAcceleration.grid(
                in_=self.liveData, row=5, columnspan=3, sticky='w')

        # Control buttons
        self.controlButtons = []
        buttonRow = 6
        maxButtonColumns = 3
        counter = 0
        for name, value in cnt.ControllerStates:
            # Tiles the buttons from left to right, up to down
            rowToPlace = buttonRow + counter//maxButtonColumns
            colToPlace = counter % maxButtonColumns
            button = tk.Button(self.mainframe,
                               text=name,
                               state="normal",
                               command=lambda v=value: self.controller.write(v)
                               )

            button.grid(row=rowToPlace, column=colToPlace)
            self.controlButtons.append(button)
            counter += 1

        self.startTime = time.time()

    def toggleAutomatic(self):
        self.isAutomatic = self.isAutomaticVar.get()
        if self.isAutomatic:
            logging.debug("Enable automatic mode")
            newState = "disabled"
        else:
            logging.debug("Disable automatic mode")
            newState = "normal"

        for button in self.controlButtons:
            button.config(state=newState)

    def refreshPorts(self, event):
        """
        Refreshes list of serial devices in dropdown
        """
        logging.debug("Refreshing ports.")
        self.availablePorts = self.controller.getAvailablePorts()

        # Delete old dropdown options
        self.portSelector["menu"].delete(0, "end")
        for value in self.availablePorts:

            def _callback(value=value):
                self.controller.updatePort(value)
                self.serialPortVar.set(value)

            self.portSelector["menu"] \
                .add_command(label=value,
                             command=_callback)
        return

    def close(self):
        """
        Cleans up, and then closes the application.
        """
        logging.info("Closing controller")
        self.controller.close()

        # Send close event to UDP thread
        logging.info("Set event to close UDP_Listener")
        self.UDP_ListenerEvent.clear()

        # Send close event to serial thread
        logging.info("Set event to close Serial_Listener")
        self.Serial_ListenerEvent.clear()

        self.master.after(0, self.master.destroy)

    def handleNavpackets(self, navPacket):
        # td = time.time() - self.startTime
        # if td > self.serialOutputRefreshPeriod/10:
        #     logging.debug("Long delay {}".format(td))
        # self.startTime = time.time()

        # Update UI
        currentTime = time.time()
        timediff = currentTime - self.last_navRefresh
        if timediff > self.serialOutputRefreshPeriod:
            self.millis["text"] = \
                "t: {:.2f}s".format(navPacket.GPS_Time)

            self.zAcceleration["text"] = \
                "az: {:.2f}m/s^2".format(navPacket.Acceleration_Z)

            self.last_navRefresh = currentTime

        # Notify controller
        if self.isAutomatic:
            self.controller.handleNavpackets(navPacket)

    def handleSerialOutputControl(self, output):
        # Update UI
        # Code to update UI will go here

        # Notify controller
        if self.isAutomatic:
            self.controller.handleSerialOutput(output)

        return


if __name__ == "__main__":
    FMT = "%(levelname)s:%(threadName)s: %(message)s < %(module)s:%(lineno)s"
    logging.basicConfig(level=logging.DEBUG, format=FMT)

    # Define thread events
    UDP_ListenerEvent = threading.Event()
    Serial_ListenerEvent = threading.Event()

    # Define controller object
    controller = cnt.Controller()

    # Set up UI
    root = tkinter.Tk()
    root.resizable(width=False, height=False)
    app = App(root, UDP_ListenerEvent, Serial_ListenerEvent, controller)

    # Create thread for UDP listener
    t1 = threading.Thread(name="UDPThread",
                          target=nav.UDP_Listener,
                          args=(app.handleNavpackets,
                                UDP_ListenerEvent))

    # Create thread for Serial listener
    t2 = threading.Thread(name="SerialThread",
                          target=controller.listen,
                          args=(app.handleSerialOutputControl,
                                Serial_ListenerEvent))

    root.protocol("WM_DELETE_WINDOW", app.close)

    try:
        t1.start()
        t2.start()
        root.mainloop()
    except KeyboardInterrupt:
        app.close()
