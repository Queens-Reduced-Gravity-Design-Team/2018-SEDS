# Queen's Reduced Gravity Design Team

The official repository for QRGX.

## Instructions
Note: All the python code assumes python 3.6+.

To install the required packages, run:
```
pip3 install -r requirements.txt
```

### Running the flight data simulation
While in the frontend directory, run:
```
python3 simulation.py
```
This will emit UDP packets to port 5125 every 0.01 seconds.


### Running the frontend
While in the frontend directory, run:
```
python3 frontend.py
```

## Directory Structure
```
controller/ - Software that will be running on the Arduino microcontroller

frontend/ - UI and UDP packet reader that will send singals to the Arduino controller.
        simulation.py - Sends UDP packets to port 5125 of simulated data
        navpacket.py - Reading the navpackets sent from the flight.
        frontend.py - Tkinter-based GUI for sending signals to microcontroller
        controller.py - Contains the protocols and thread-safe handling for interfacing with the controller
```

## Documentation
### Controller

#### Threads
The frontend runs on three separate threads, a serial listener, UDP listener and UI thread.
The UI thread is the default thread when beginning a python process. When the UI is closed,
the other threads should safely exit. This is done by using a thread-safe Event object, which
notifies the other threads to close. However, this may cause the process to continue for a few
seconds even after the window is closed.

The `controller.Controller` object tries to maintain synchronization by using simple thread-locking. This may
cause issues if many different write requests are sent at the same time.

#### UDP Pitfalls
The unfortunate reality of UDP is that there is no guarantee that the data packets arrive in order,
and are uncorrupt. The way it is handled right now, exactly 88 bytes are read, and the values are
within the expected range. Though this doesn't guarantee that any bytes were swapped, it does provide
some defree of sanity

This can cause issues if packets arrive in the wrong order, or if only a partially transmitted message is sent.

### Simulation
Running the simulator will loop over a sample file and emit UDP packets to port 5125
at a frequency of 100Hz.

## Protocol
In the codebase, "input" corresponds to data going from the frontend to the controller.

```
Input: 4 byte integer corresponding to a particular state. The states in frontend/controller.py and
controller/main.ino must be identical

DO_NOTHING = 0      As name implies, does not do anything.
EMERGENCY_STOP = 1  This state should disable all active components and should guarantee a physically safe stae.
TEST_LED_ON = 2     Enable the built in LED
TEST_LED_OFF = 3    Disable the built in LED
```
