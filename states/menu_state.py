import asyncio
import gc

from data.config import ColorConfig, Config
from hardware.buttons import Buttons
from states.state_utils import SelectableList


class MenuState:
    def __init__(self, hardware, menu_data):
        self.hw = hardware
        self.current_menu = menu_data
        self.menu_stack = []
        self.config = Config()

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
                        fingering_color=payload.get("fingering_color")
                    )
                elif item_type == "scale_drill":
                    payload = selected_item.get("payload", {})
                    from states.scale_drill_state import ScaleDrillState
                    next_state = ScaleDrillState(self.hw, payload, self.config)
                    await next_state.run()
                    del next_state
                    gc.collect()
                    self.hw.display.root_group = self.selectable_list.ui_group
                elif item_type == "play":
                    from states.play_state import PlayState
                    next_state = PlayState(self.hw, self.config)
                    await next_state.run()
                    del next_state
                    gc.collect()
                    self.hw.display.root_group = self.selectable_list.ui_group
                elif item_type == "song":
                    payload = selected_item.get("payload", {})
                    from states.song_state import SongState
                    next_state = SongState(self.hw, payload, self.config)
                    await next_state.run()
                    del next_state
                    gc.collect()
                    self.hw.display.root_group = self.selectable_list.ui_group
                else:
                    print(f"Error: Unhandled menu type '{item_type}'")

            await asyncio.sleep(0.01)
