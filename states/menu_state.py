import asyncio
import gc

import displayio
import terminalio
from adafruit_display_text import label

from hardware.buttons import Buttons


class MenuState:
    def __init__(self, hardware, menu_data):
        self.hw = hardware
        self.current_menu = menu_data
        self.menu_stack = []
        self.selected_index = 0

        self.ui_group = displayio.Group()
        self.hw.display.root_group = self.ui_group
        self.labels = []

        self.title_label = label.Label(terminalio.FONT, text="", color=0x00AAFF, scale=3, x=10, y=20)
        self.ui_group.append(self.title_label)

        self.render_menu()

    def render_menu(self):
        while len(self.ui_group) > 1:
            self.ui_group.pop()

        self.labels = []
        header_text = self.current_menu.get("title", self.current_menu.get("text", "MENU"))
        self.title_label.text = header_text

        for i, item in enumerate(self.current_menu["items"]):
            is_selected = (i == self.selected_index)
            color = 0x00FF00 if is_selected else 0xFFFFFF
            prefix = "> " if is_selected else "  "

            lbl = label.Label(terminalio.FONT, text=f"{prefix}{item['text']}", color=color, scale=2, x=20,
                              y=80 + (i * 35))
            self.labels.append(lbl)
            self.ui_group.append(lbl)

    def update_selection_ui(self):
        for i, lbl in enumerate(self.labels):
            if i == self.selected_index:
                lbl.color = 0x00FF00
                lbl.text = "> " + self.current_menu["items"][i]["text"]
            else:
                lbl.color = 0xFFFFFF
                lbl.text = "  " + self.current_menu["items"][i]["text"]

    async def run(self):
        while True:
            self.hw.update_button_states()

            if Buttons.R_1.just_pressed:
                self.selected_index = (self.selected_index - 1) % len(self.current_menu["items"])
                self.update_selection_ui()
            elif Buttons.R_2.just_pressed:
                self.selected_index = (self.selected_index + 1) % len(self.current_menu["items"])
                self.update_selection_ui()
            elif Buttons.L_SELECT.just_pressed:
                selected_item = self.current_menu["items"][self.selected_index]
                item_type = selected_item.get("type")

                if item_type == "back":
                    if self.menu_stack:
                        self.current_menu = self.menu_stack.pop()
                        self.selected_index = 0
                        self.render_menu()

                elif item_type == "menu":
                    if "items" in selected_item and len(selected_item["items"]) > 0:
                        self.menu_stack.append(self.current_menu)
                        self.current_menu = selected_item
                        self.selected_index = 0
                        self.render_menu()
                    else:
                        print(f"Warning: '{selected_item.get('text')}' has no items!")

                elif item_type == "scale_drill":
                    payload = selected_item.get("payload", {})
                    from states.scale_drill_state import ScaleDrillState
                    next_state = ScaleDrillState(self.hw, payload)
                    await next_state.run()
                    del next_state
                    gc.collect()
                    self.hw.display.root_group = self.ui_group
                elif item_type == "play":
                    from states.play_state import PlayState
                    next_state = PlayState(self.hw)
                    await next_state.run()
                    del next_state
                    gc.collect()
                    self.hw.display.root_group = self.ui_group
                else:
                    print(f"Error: Unhandled menu type '{item_type}'")

            await asyncio.sleep(0.01)
