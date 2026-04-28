import asyncio
import os

import terminalio
from adafruit_display_text import label

from data.config import ButtonPin
from hardware.buttons import ButtonHardwareSource, Buttons
from states.play_state import PlayState

CALIBRATE_PATH = "/CALIBRATE"

# Right hand first, then left, then SELECT.
CALIBRATION_ORDER = (
    "R_F_SHARP", "R_HIGH_F_SHARP", "R_C", "R_E", "R_1", "R_2", "R_3",
    "R_B_FLAT", "R_LOW_E_FLAT", "R_LOW_C",
    "L_OCTAVE", "L_FRONT_F", "L_1", "L_2", "L_3",
    "L_B_FLAT", "L_D", "L_E_FLAT", "L_F", "L_G_SHARP",
    "L_LOW_C_SHARP", "L_LOW_B", "L_LOW_B_FLAT",
    "L_SELECT",
)


def calibrate_requested() -> bool:
    try:
        os.stat(CALIBRATE_PATH)
        return True
    except OSError:
        return False


class CalibrationState(PlayState):
    def __init__(self, hw, config):
        super().__init__(hw, config, title="Calibration")
        self.config = config

        # Drop the staff — we use that area for prompts.
        if self.staff in self.ui_group:
            self.ui_group.remove(self.staff)

        fg = config.color_data.fg_color
        self.press_label = label.Label(terminalio.FONT, text="Press:", color=fg, scale=1)
        self.press_label.anchor_point = (0.5, 0.5)
        self.press_label.anchored_position = (105, 95)
        self.ui_group.append(self.press_label)

        self.prompt_label = label.Label(terminalio.FONT, text="", color=fg, scale=2)
        self.prompt_label.anchor_point = (0.5, 0.5)
        self.prompt_label.anchored_position = (105, 115)
        self.ui_group.append(self.prompt_label)

        self.progress_label = label.Label(terminalio.FONT, text="", color=fg, scale=1)
        self.progress_label.anchor_point = (0.5, 1.0)
        self.progress_label.anchored_position = (105, 230)
        self.ui_group.append(self.progress_label)

    def _read_grounded_pin(self):
        """Returns the (hw_source, hw_pin) of the first grounded pin, or None."""
        gpio1 = self.hw.mcp1.gpio
        for pin in range(16):
            if not (gpio1 >> pin) & 1:
                return (ButtonHardwareSource.MCP1, pin)
        gpio2 = self.hw.mcp2.gpio
        for pin in range(16):
            if not (gpio2 >> pin) & 1:
                return (ButtonHardwareSource.MCP2, pin)
        return None

    async def _wait_for_release(self) -> None:
        while self._read_grounded_pin() is not None:
            await asyncio.sleep(0.01)

    async def _wait_for_press(self):
        while True:
            pressed = self._read_grounded_pin()
            if pressed is not None:
                return pressed
            await asyncio.sleep(0.01)

    async def run(self) -> None:
        if self.hw.display.root_group != self.ui_group:
            self.hw.display.root_group = self.ui_group
        if self.chart_sprite not in self.ui_group:
            self.ui_group.append(self.chart_sprite)

        used = set()
        total = len(CALIBRATION_ORDER)

        for index, name in enumerate(CALIBRATION_ORDER):
            button = getattr(Buttons, name)
            self.prompt_label.text = name
            self.progress_label.text = f"{index + 1} / {total}"

            if button.bounding_box is not None:
                await self.blit_specific_fingering((button,))
            self.hw.display.refresh()

            await self._wait_for_release()

            while True:
                pressed = await self._wait_for_press()
                if pressed not in used:
                    break
                # Duplicate — prompt and wait for them to release + try again.
                self.prompt_label.text = "DUPE-" + name
                self.hw.display.refresh()
                await self._wait_for_release()
                self.prompt_label.text = name
                self.hw.display.refresh()

            hw_source, hw_pin = pressed
            setattr(self.config.button_data, name, ButtonPin(hw_source, hw_pin))
            used.add(pressed)

            await self._wait_for_release()
            if button.bounding_box is not None:
                await self.clear_specific_fingering((button,))

        self.config.persist()
        Buttons.apply_config(self.config.button_data)
        try:
            os.remove(CALIBRATE_PATH)
        except OSError as e:
            print(f"Could not remove {CALIBRATE_PATH}: {e}")

        self.prompt_label.text = "Done!"
        self.progress_label.text = ""
        self.hw.display.refresh()
        await asyncio.sleep(1.5)
