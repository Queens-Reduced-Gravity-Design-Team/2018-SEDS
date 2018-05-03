import serial
from serial.tools import list_ports
import tkinter as tk
from tkinter import Label, Button, Tk, OptionMenu
import logging


class AppState:
    def __init__(self):
        self.currentPort = None


class App:
    def __init__(self, master):
        # State of the current UI
        self.state = AppState()

        self.master = master
        master.title("Control Panel")

        self.label = Label(master, text="Ugly Controller V1.0")
        self.label.grid(row=0, column=1)

        # Serial port label
        self.label = Label(master, text="Serial Port")
        self.label.grid(row=1, column=0)

        # Serial port dropdown
        self.serialPortVar = tk.StringVar()
        self.serialPortVar.set("")
        self.portSelector = \
            OptionMenu(self.master, self.serialPortVar, "")
        self.portSelector.configure(width=18)
        self.portSelector.bind("<Button-1>", self.refreshPorts)
        self.portSelector.grid(row=1, column=1)

        # Selector for automatic mode
        self.isAutomatic = tk.BooleanVar()
        self.isAutomatic.set(False)
        self.checkButton = tk.Checkbutton(
            master, text="Automatic Mode", variable=self.isAutomatic,
            state=tk.NORMAL, onvalue=True, offvalue=False)
        self.checkButton.grid(row=1, column=3)

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
        logging.debug("UI:Refreshing ports.")
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
        currentPort = self.state.currentPort
        if currentPort is not None:
            logging.debug("UI:Closing serial port {}".format(currentPort.name))
            currentPort.close()

        logging.debug("UI:Opening new port {}".format(value))
        currentPort = serial.Serial(value)
        self.state.currentPort = currentPort
        self.serialPortVar.set(value)

    def close(self):
        """
        Cleans up, and then closes the application.
        """
        currentPort = self.state.currentPort
        logging.info("UI:Closing connection")
        if currentPort is not None:
            logging.debug("UI:Closing serial port {}".format(currentPort.name))
            currentPort.close()

        self.master.destroy()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    root = Tk()
    app = App(root)
    root.mainloop()
