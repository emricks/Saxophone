import asyncio

from hardware.buttons import Buttons
from states.state_utils import SelectableList


class BreathSettingsState:
    """Settings screen for the per-install breath threshold. Mirrors
    VolumeSettingsState — title reflects the live value, items are pure
    actions. Applies the new threshold to the running breath sensor
    immediately (it reads the value each poll) and persists on Back."""

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
        return f"Breath {self.config.breath_data.threshold:.1f} hPa"

    def _apply(self):
        self.hw.breath_sensor.threshold = self.config.breath_data.threshold
        self.selectable_list.title_label.text = self._title()
        self._dirty = True

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
                    self.config.breath_data.step_up()
                    self._apply()
                elif action == "down":
                    self.config.breath_data.step_down()
                    self._apply()
                elif action == "back":
                    if self._dirty:
                        self.config.persist()
                    return

            await asyncio.sleep(0.01)