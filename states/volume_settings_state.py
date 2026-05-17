import asyncio

from hardware.buttons import Buttons
from states.state_utils import SelectableList


class VolumeSettingsState:
    def __init__(self, hw, config):
        self.hw = hw
        self.config = config
        self._dirty = False

        self.items = [
            {"text": "Up", "action": "up"},
            {"text": "Down", "action": "down"},
            {"text": "< Back", "action": "back"},
        ]

        self.selectable_list = SelectableList(title=self._title(), config=config)
        self.hw.display.root_group = self.selectable_list.ui_group
        self.selectable_list.set_items(self.items, title=self._title())

    def _title(self):
        return f"Volume {self.config.volume_data.percent()}%"

    async def _apply_volume(self):
        volume = self.config.volume_data.volume
        self.hw.mixer.voice[0].level = volume
        self.hw.mixer.voice[1].level = volume
        self.selectable_list.title_label.text = self._title()
        self._dirty = True
        self.hw.play_note(50)  # A4 preview tone
        await asyncio.sleep(0.2)
        await self.hw.stop_note()

    async def run(self):
        while True:
            self.hw.update_button_states()

            if Buttons.R_1.just_pressed:
                self.selectable_list.move_up()
            elif Buttons.R_2.just_pressed:
                self.selectable_list.move_down()
            elif Buttons.L_SELECT.just_pressed:
                action = self.selectable_list.get_selected_item().get("action")
                if action == "up":
                    self.config.volume_data.step_up()
                    await self._apply_volume()
                elif action == "down":
                    self.config.volume_data.step_down()
                    await self._apply_volume()
                elif action == "back":
                    if self._dirty:
                        self.config.persist()
                    return

            await asyncio.sleep(0.01)
