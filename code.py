# code.py
import asyncio
from hardware.saxophone import SaxHardware
from states.menu_state import MenuState
from data.menu_config import MAIN_MENU
from data.config import Config


async def main():
    config = Config.load_config()

    hw = SaxHardware()
    await hw.start_hardware()

    initial_state = MenuState(hw, MAIN_MENU, config)

    # Run the state
    await initial_state.run()


# Start the asyncio event loop
asyncio.run(main())
