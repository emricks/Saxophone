import asyncio
import gc

from data.config import ColorConfig
from hardware.buttons import Buttons
from states.state_utils import SelectableList


class MenuState:
    def __init__(self, hardware, menu_data, config):
        self.hw = hardware
        self.current_menu = menu_data
        self.menu_stack = []
        self.config = config

        # The selectable list handles drawing items and selection logic
        header_text = self.current_menu.get("title", self.current_menu.get("text", "MENU"))
        self.selectable_list = SelectableList(title=header_text)
        
        # We hook the SelectableList's UI group to the display
        self.hw.display.root_group = self.selectable_list.ui_group

        self.selectable_list.set_items(self.current_menu["items"], title=header_text)

    async def run(self):
        while True:
            self.hw.update_button_states()

            if Buttons.R_1.just_pressed:
                self.selectable_list.move_up()
            elif Buttons.R_2.just_pressed:
                self.selectable_list.move_down()
            elif Buttons.L_SELECT.just_pressed:
                selected_item = self.selectable_list.get_selected_item()
                if not selected_item:
                    continue
                    
                item_type = selected_item.get("type")

                if item_type == "back":
                    if self.menu_stack:
                        self.current_menu = self.menu_stack.pop()
                        header_text = self.current_menu.get("title", self.current_menu.get("text", "MENU"))
                        self.selectable_list.set_items(self.current_menu["items"], title=header_text)

                elif item_type == "menu":
                    if "items" in selected_item and len(selected_item["items"]) > 0:
                        self.menu_stack.append(self.current_menu)
                        self.current_menu = selected_item
                        header_text = self.current_menu.get("title", self.current_menu.get("text", "MENU"))
                        self.selectable_list.set_items(self.current_menu["items"], title=header_text)
                    else:
                        print(f"Warning: '{selected_item.get('text')}' has no items!")

                elif item_type == "color":
                    payload = selected_item.get("payload")
                    self.config.color_data = ColorConfig(
                        name=payload.get("name"),
                        fg_color=payload.get("fg_color"),
                        bg_color=payload.get("bg_color"),
                        chart_color=payload.get("chart_color"),
                        fingering_color=payload.get("fingering_color"),
                        drill_note_color=payload.get("drill_note_color")
                    )
                    self.config.persist()
                elif item_type == "scale_drill":
                    payload = selected_item.get("payload", {})
                    from states.scale_drill_state import ScaleDrillState
                    await self._transition_to_state(ScaleDrillState, payload)
                elif item_type == "play":
                    from states.play_state import PlayState
                    await self._transition_to_state(PlayState)
                elif item_type == "song":
                    payload = selected_item.get("payload", {})
                    from states.song_state import SongState
                    await self._transition_to_state(SongState, payload)
                else:
                    print(f"Error: Unhandled menu type '{item_type}'")

            await asyncio.sleep(0.01)

    async def _transition_to_state(self, state_class, payload=None):
        """Helper to clear display and transition to a new state."""
        # Clear display immediately to avoid showing old menu during loading
        self.hw.display.root_group = None
        await asyncio.sleep(0)

        if payload is not None:
            next_state = state_class(self.hw, payload, self.config)
        else:
            next_state = state_class(self.hw, self.config)

        await next_state.run()
        del next_state
        gc.collect()
        # Restore the menu UI
        self.hw.display.root_group = self.selectable_list.ui_group
