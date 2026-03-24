# hardware.py
import board
import busio
import digitalio
import displayio
import fourwire
import adafruit_ili9341
import keypad


class SaxHardware:
    def __init__(self):
        displayio.release_displays()

        # --- Display Setup (Verified Working) ---
        self.spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        self.tft_cs = board.MISO
        self.tft_dc = board.RX
        self.tft_rst = board.D4

        self.backlight = digitalio.DigitalInOut(board.TX)
        self.backlight.direction = digitalio.Direction.OUTPUT
        self.backlight.value = True

        self.display_bus = fourwire.FourWire(
            self.spi, command=self.tft_dc, chip_select=self.tft_cs, reset=self.tft_rst
        )
        self.display = adafruit_ili9341.ILI9341(self.display_bus, width=320, height=240)

        # --- Navigation Buttons ---
        # Wiring: Connect buttons from these pins to GND
        self.nav_pins = (board.D11, board.D13, board.D12)

        # 2. Dynamically assign the logical roles based on the pin's actual position
        self.BTN_UP = self.nav_pins.index(board.D11)
        self.BTN_SELECT = self.nav_pins.index(board.D13)
        self.BTN_DOWN = self.nav_pins.index(board.D12)

        self.keys = keypad.Keys(self.nav_pins, value_when_pressed=False, pull=True)

    def get_button_event(self):
        """Returns the next event in the keypad queue, or None."""
        return self.keys.events.get()