# Sample MCP1 at boot. If 3+ buttons are held, stay in dev mode so the host
# can write to CIRCUITPY (you can edit code.py over USB). Otherwise remount
# the filesystem device-writable so code.py can persist config.json.

import board
import digitalio
import storage
import time

from adafruit_mcp230xx.mcp23017 import MCP23017

DEV_MODE_THRESHOLD = 2

try:
    i2c = board.STEMMA_I2C()
    mcp1 = MCP23017(i2c, address=0x20)

    # Configure all 16 GPIO pins as input with pull-ups so unpressed reads high.
    for pin_num in range(16):
        pin = mcp1.get_pin(pin_num)
        pin.direction = digitalio.Direction.INPUT
        pin.pull = digitalio.Pull.UP

    time.sleep(0.05)  # let pull-ups settle

    gpio = mcp1.gpio
    grounded = sum(1 for n in range(16) if not (gpio >> n) & 1)
except Exception as e:
    # Default to dev mode on hardware fault so a broken MCP can't lock you out.
    print(f"boot.py: could not sample MCP1 ({e}); defaulting to dev mode")
    grounded = DEV_MODE_THRESHOLD

if grounded >= DEV_MODE_THRESHOLD:
    print(f"boot.py: {grounded} buttons held on MCP1 - dev mode (host-writable)")
else:
    storage.remount("/", readonly=False)
    print(f"boot.py: run mode (device-writable); {grounded} buttons held")
