import asyncio

from hardware.buttons import Buttons
from states.play_state import PlayState


class ScaleDrillState(PlayState):
    def __init__(self, hardware, payload, config):
        self.drill_name = payload.get("name", "Unknown Drill")
        super().__init__(hardware, config, title=self.drill_name)
        self.notes = payload.get("notes", [])

    async def run(self):
        while self.is_running:
            self.hw.update_button_states()

            if Buttons.L_SELECT.just_pressed:
                # exit if select button pressed
                self.is_running = False
                break

            await asyncio.sleep(0.001)