# saxophone.py
import array

import board
import busio
import digitalio
import displayio
import fourwire
import adafruit_ili9341
import keypad
import audiobusio
import synthio
import audiomixer
from adafruit_mcp230xx.mcp23017 import MCP23017

from hardware.buttons import ButtonHardwareSource, Buttons
from data.notes import note_from_mask


class SaxHardware:
    def __init__(self):
        displayio.release_displays()

        # --- Display Setup  ---
        print("Initializing display...")
        self.spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        self.tft_cs = board.MISO
        self.tft_dc = board.RX
        self.tft_rst = board.D4

        self.backlight = digitalio.DigitalInOut(board.TX)
        self.backlight.direction = digitalio.Direction.OUTPUT
        self.backlight.value = True

        self.display_bus = fourwire.FourWire(
            self.spi, command=self.tft_dc, chip_select=self.tft_cs, reset=self.tft_rst, baudrate=62500000
        )
        self.display = adafruit_ili9341.ILI9341(self.display_bus, width=320, height=240)
        print("Display initialized!")
        # --- Audio Setup ---
        print("Initializing audio...")
        # 1. Turn on the Prop-Maker's I2S Amplifier
        self.audio_enable = digitalio.DigitalInOut(board.EXTERNAL_POWER)
        self.audio_enable.direction = digitalio.Direction.OUTPUT
        self.audio_enable.value = True

        # 2. Set up the I2S Bus
        self.audio = audiobusio.I2SOut(
            bit_clock=board.I2S_BIT_CLOCK,
            word_select=board.I2S_WORD_SELECT,
            data=board.I2S_DATA
        )

        # 3. Create the Mixer and play it on the audio bus
        self.mixer = audiomixer.Mixer(
            voice_count=1,
            sample_rate=22050,
            channel_count=1,
            bits_per_sample=16,
            samples_signed=True
        )
        self.audio.play(self.mixer)

        # 4. Initialize the Synthesizer and attach it to the mixer
        self.synth = synthio.Synthesizer(sample_rate=22050)
        # type: ignore (or # noinspection PyTypeChecker)
        self.mixer.voice[0].play(self.synth)

        # 5. Set Master Volume
        self.mixer.voice[0].level = 0.3

        # 6. The Breath (Envelope)
        self.sax_envelope = synthio.Envelope(
            attack_time=0.1,  # 100ms fade-in
            decay_time=0.0,
            release_time=0.0,
            attack_level=1.0,
            sustain_level=1.0
        )

        # 7. The Tone (Waveform)
        self.sax_waveform = self.load_wav_buffer("../data/audio/AKWF_altosax_0001.wav")
        print("Audio initialized!")

        # --- Buttons ---
        # --- I2C MCP23017 Setup ---
        print("Initializing MCP at address 0x27")
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.mcp = MCP23017(self.i2c, address=0x27)

        self.onboard_buttons = [btn for btn in Buttons.ALL if btn.hw_source == ButtonHardwareSource.ONBOARD]
        self.mcp_buttons = [btn for btn in Buttons.ALL if btn.hw_source == ButtonHardwareSource.MCP]

        # Initialize the pins for buttons managed by MCP GPIO
        for btn in self.mcp_buttons:
            pin = self.mcp.get_pin(btn.hw_pin)
            pin.direction = digitalio.Direction.INPUT
            pin.pull = digitalio.Pull.UP
        print("Initalized MCP")

        # initialize the pins for buttons managed by onboard GPIO
        print("Initializing Onboard GPIO")
        onboard_pins = tuple(btn.hw_pin for btn in self.onboard_buttons)
        # keypad library manages our onboard_pins
        self.onboard_button_keys = keypad.Keys(onboard_pins, value_when_pressed=False, pull=True)
        print("Initialized onboard GPIO")

    def stop_note(self):
        """Releases all active notes to trigger the fade-out envelope."""
        self.synth.release_all()

    def play_note(self, midi_number):
        """Converts a MIDI integer to Hertz and plays it with the sax waveform."""
        freq = 440.0 * (2.0 ** ((midi_number - 69) / 12))
        note = synthio.Note(
            frequency=freq,
            envelope=self.sax_envelope,
            waveform=self.sax_waveform
        )
        self.synth.press(note)

    def load_wav_buffer(self, filename):
        """Hacks a standard 16-bit mono WAV file directly into a raw array."""
        try:
            with open(filename, "rb") as f:
                f.seek(44)  # Skip the 44-byte standard header

                # The AKWF documentation states the audio is exactly 600 samples.
                # 600 samples * 2 bytes (16-bit) = 1200 bytes.
                raw_bytes = f.read(1200)

                return array.array('h', raw_bytes)
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
            return None

    def update_button_states(self):
        """Updates the unified button_states array with both onboard and I2C pins."""
        # 1. Update the 'was_pressed' state for all buttons BEFORE polling new data
        for btn in Buttons.ALL:
            btn.was_pressed = btn.is_pressed

        # 2. process onboard GPIO from the keypad library to set key states
        while True:
            event = self.onboard_button_keys.events.get()
            if not event:
                break
            # translate keypad event to the name of the button and update our button state
            button_def = self.onboard_buttons[event.key_number]
            button_def.is_pressed = event.pressed

        # 3. Poll the MCP GPIO and set button states
        mcp_register = self.mcp.gpio
        for btn in self.mcp_buttons:
            # If the bit is 0, it is pulled to ground (pressed)
            btn.is_pressed = not (mcp_register & (1 << btn.hw_pin))

        # DEBUG - print buttons just pressed
        for btn in Buttons.ALL:
            if btn.just_pressed:
                print(f"Button on hardware {btn.hw_source} pin {btn.hw_pin} pressed")

    def get_fingering_mask(self):
        """Builds the mask from all currently pressed buttons that have a fingering_bit."""
        mask = 0
        for btn in Buttons.ALL:
            if btn.fingering_bit is not None and btn.is_pressed:
                mask |= (1 << btn.fingering_bit)
        return mask

    def get_current_note(self):
        return note_from_mask(self.get_fingering_mask())