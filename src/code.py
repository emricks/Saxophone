# code.py
import asyncio
from hardware import SaxHardware
from states.menu_state import MenuState
from data.menu_config import MAIN_MENU


async def main():
    # Initialize hardware abstraction
    hw = SaxHardware()

    # Initialize the first state, passing in hardware and data
    initial_state = MenuState(hw, MAIN_MENU)

    # Run the state
    await initial_state.run()


# Start the asyncio event loop
asyncio.run(main())