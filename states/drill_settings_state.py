import asyncio

from hardware.buttons import Buttons
from states.state_utils import SelectableList


class DrillSettingsState:
    """Settings screen for persisted drill defaults (BPM, mode). Mirrors
    VolumeSettingsState — title reflects the live values, items are pure
    actions. Changes also write through to ScaleDrillState.SESSION_MODE so
    the toggle takes effect this session, not just next boot."""

    def __init__(self, hw, config):
        self.hw = hw
        self.config = config
        self._dirty = False

        self.items = [
            {"text": "< Back",       "action": "back"},
            {"text": "Toggle Mode",  "action": "toggle_mode"},
            {"text": "BPM Up",       "action": "bpm_up"},
            {"text": "BPM Down",     "action": "bpm_down"},
        ]

        self.selectable_list = SelectableList(title=self._title(), config=config)
        self.hw.display.root_group = self.selectable_list.ui_group
        self.selectable_list.set_items(self.items, title=self._title())

    def _title(self):
        drill = self.config.drill_data
        return f"BPM {drill.default_bpm}  {drill.default_mode.upper()}"

    def _apply_session_mode(self):
        # Import here to avoid a circular import at module-load time.
        from states.scale_drill_state import ScaleDrillState
        ScaleDrillState.SESSION_MODE = self.config.drill_data.default_mode

    def _refresh_title(self):
        self.selectable_list.title_label.text = self._title()

    async def run(self):
        while True:
            self.hw.update_button_states()

            if Buttons.R_1.just_pressed:
                self.selectable_list.move_up()
            elif Buttons.R_2.just_pressed:
                self.selectable_list.move_down()
            elif Buttons.L_SELECT.just_pressed:
                action = self.selectable_list.get_selected_item().get("action")
                if action == "toggle_mode":
                    self.config.drill_data.toggle_mode()
                    self._apply_session_mode()
                    self._dirty = True
                    self._refresh_title()
                elif action == "bpm_up":
                    self.config.drill_data.step_bpm_up()
                    self._dirty = True
                    self._refresh_title()
                elif action == "bpm_down":
                    self.config.drill_data.step_bpm_down()
                    self._dirty = True
                    self._refresh_title()
                elif action == "back":
                    if self._dirty:
                        self.config.persist()
                    return

            await asyncio.sleep(0.01)