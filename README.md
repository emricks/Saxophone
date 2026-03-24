# Saxophone Drill

A project to build a tool that provides fingering practice for the saxophone.

## Hardware Setup
This code base runs on an Adafruit Feather RP2040
TODO

## Installation
After plugging in the Feather, you must ensure CircuitPython is installed following the [documentation](https://learn.adafruit.com/adafruit-feather-rp2040-pico/circuitpython).

A few libraries need to be copied to the device one time, into the 'lib' directory.
These are installable using 'circup'. A convenience make target `make setup-device` will
install these for you.

Finally, `make deploy` will copy the current code state to the device. By default, this
deploys to `/Volumes/CIRCUITPY` but you can specify a path using `make deploy DEST=[path-to-feather-mount]`.

## Development
This code base is developed in PyCharm. After opening the project with a
standard python virtual environment (e.g. 3.12), open a terminal in PyCharm
and run `make deps` to install the CircuitPython dependencies into your virtual environment.

Documentation around developing the UI can be found in the [displayio](https://learn.adafruit.com/circuitpython-display-support-using-displayio/introduction) docs.

The code uses asyncio to 

### Structure

Every "screen" on the display is a "state" which implements an async `run()` method. There is always one active state, 
and the user jumps around between states to navigate the UI. For example, the MenuState class has a `run()` 
method that simply draws a list of the child states and detects button presses. When a user selects a child 
state using these buttons, it replaces the current MenuState with the new child MenuState or a new activity
like a DrillState, which then gets its `run()` method called to draw the new UI. Similarly, the "back" button 
replaces the current state with its parent state. This is implemented by saving a "menu stack", when a MenuState is
replaced it is appended to the stack, and when the back button is pressed the previous state is popped off the stack.

The code uses `asyncio` to perform non-blocking audio and UI updates. This means the state `run()` methods need
to be async and its logic needs to run a `while` loop forever until some user action changes state.

The structure of the states is managed by `data/menu_config.py`. New states can be added by modifying this
structure, defining the state's type and other parameters. There are MenuStates, DrillStates, and others.

```
src/
├── code.py             # main entrypoint of program
├── hardware.py         # hardware setup and access methods
└── data/menu_config.py # config-driven system for creating states
└── states/
    ├── drill_state.py  # behavior of drill exercises
    └── menu_state.py   # behavior of menus
```