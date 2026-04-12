import displayio
import terminalio
from adafruit_display_text import label

class SelectableList:
    def __init__(self, title=""):
        self.items = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_items = 4
        self.title = title
        
        self.ui_group = displayio.Group()
        self.labels = []
        
        self.title_label = label.Label(terminalio.FONT, text=self.title, color=0x00AAFF, scale=3, x=10, y=20)
        self.ui_group.append(self.title_label)
        
    def set_items(self, items, title=None):
        self.items = items
        if title is not None:
            self.title = title
            self.title_label.text = self.title
        self.selected_index = 0
        self.scroll_offset = 0
        self.render()

    def render(self):
        while len(self.ui_group) > 1:
            self.ui_group.pop()

        self.labels = []
        
        start_index = self.scroll_offset
        end_index = min(len(self.items), self.scroll_offset + self.max_visible_items)

        for i in range(start_index, end_index):
            item = self.items[i]
            # Handle if items are dicts or objects
            text = item.get("text", str(item)) if isinstance(item, dict) else str(item)
            is_selected = (i == self.selected_index)
            color = 0x00FF00 if is_selected else 0xFFFFFF
            prefix = "> " if is_selected else "  "

            y_pos = 80 + ((i - self.scroll_offset) * 35)
            lbl = label.Label(terminalio.FONT, text=f"{prefix}{text}", color=color, scale=2, x=20,
                              y=y_pos)
            self.labels.append(lbl)
            self.ui_group.append(lbl)

        # Scrolling indicators (arrows)
        if self.scroll_offset > 0:
            up_arrow = label.Label(terminalio.FONT, text="^", color=0xAAAAAA, scale=2, x=40, y=60)
            self.ui_group.append(up_arrow)

        has_more_below = len(self.items) > end_index

        if has_more_below:
            last_visible_idx = end_index - 1
            down_y = min(80 + ((last_visible_idx - self.scroll_offset) * 35) + 35, 220)
            down_arrow = label.Label(terminalio.FONT, text="v", color=0xAAAAAA, scale=2, x=40, y=down_y)
            self.ui_group.append(down_arrow)

    def move_up(self):
        if not self.items: return
        self.selected_index = (self.selected_index - 1) % len(self.items)
        self.update_selection_ui()

    def move_down(self):
        if not self.items: return
        self.selected_index = (self.selected_index + 1) % len(self.items)
        self.update_selection_ui()
        
    def get_selected_item(self):
        if not self.items: return None
        return self.items[self.selected_index]

    def update_selection_ui(self):
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_index - self.max_visible_items + 1
        self.render()
