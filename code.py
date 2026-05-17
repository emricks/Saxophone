# code.py
import asyncio
import gc

from hardware.saxophone import SaxHardware
from states.calibration_state import CalibrationState, calibrate_requested
from states.menu_state import MenuState
from data.menu_config import MAIN_MENU
from data.config import Config


async def main():
    config = Config.load_config()

    # Seed the live drill mode from the persisted default. The ready-screen
    # toggle in ScaleDrillState mutates SESSION_MODE for the rest of the
    # session; this restores it on boot.
    from states.scale_drill_state import ScaleDrillState
    ScaleDrillState.SESSION_MODE = config.drill_data.default_mode

    hw = SaxHardware(config)
    await hw.start_hardware()

    if calibrate_requested():
        calibration = CalibrationState(hw, config)
        await calibration.run()
        del calibration
        gc.collect()

    initial_state = MenuState(hw, MAIN_MENU, config)

    # Run the state
    await initial_state.run()


# Start the asyncio event loop
asyncio.run(main())
