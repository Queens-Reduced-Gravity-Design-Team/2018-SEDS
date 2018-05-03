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
python3 simulation.py
```

## Directory Structure
```
controller/ - Software that will be running on the Arduino microcontroller

frontend/ - UI and UDP packet reader that will send singals to the Arduino controller.
        simulation.py - Sends UDP packets to port 5125 of simulated data
        navpacket.py - Reading the navpackets sent from the flight.
        frontend.py - Tkinter-based GUI for sending signals to microcontroller
```

## Documentation
### Controller
### Frontend
### Simulation

## Protocol
