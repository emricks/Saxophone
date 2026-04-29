# saxophone.py
import array
import board
import busio
import asyncio
import digitalio
import displayio
import fourwire
import adafruit_ili9341
import keypad
import audiobusio
import synthio
import audiomixer
from adafruit_mcp230xx.mcp23017 import MCP23017

from data.config import Config
from hardware.breath import BreathSensor
from hardware.buttons import ButtonHardwareSource, Buttons
from composer.notes import note_from_mask


class SaxHardware:
    NOTE_RELEASE_TIME = 0.05

    def __init__(self, config: Config):
        displayio.release_displays()

        # --- Display Setup  ---
        print("Initializing display...")
        self.spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        self.tft_cs = board.MISO
        self.tft_dc = board.RX
        self.tft_rst = board.D25

        self.backlight = digitalio.DigitalInOut(board.TX)
        self.backlight.direction = digitalio.Direction.OUTPUT
        self.backlight.value = True

        self.display_bus = fourwire.FourWire(
            self.spi, command=self.tft_dc, chip_select=self.tft_cs, reset=self.tft_rst, baudrate=32000000
        )
        self.display = adafruit_ili9341.ILI9341(self.display_bus, width=320, height=240)
        print("Display initialized!")

        # --- Audio Setup ---
        print("Initializing audio...")
        # Set up the I2S Bus
        self.audio = audiobusio.I2SOut(
            bit_clock=board.D5,
            word_select=board.D6,
            data=board.D9
        )

        # 3. Create the Mixer and play it on the audio bus
        self.mixer = audiomixer.Mixer(
            voice_count=2,
            sample_rate=22050,
            channel_count=1,
            bits_per_sample=16,
            samples_signed=True,
            buffer_size=6144
        )
        self.audio.play(self.mixer)

        # 4. Initialize the Synthesizer and attach it to the mixer
        self.synth = synthio.Synthesizer(sample_rate=22050)
        # type: ignore (or # noinspection PyTypeChecker)
        self.mixer.voice[0].play(self.synth)

        # 5. Set Master Volume
        self.mixer.voice[0].level = config.volume_data.volume

        # 6. The Breath (Envelope)
        self.sax_envelope = synthio.Envelope(
            attack_time=0.05,  # 50ms fade-in
            decay_time=0.0,
            release_time=SaxHardware.NOTE_RELEASE_TIME,
            attack_level=1.0,
            sustain_level=0.8
        )

        # 7. The Tone (Waveform)
        self.sax_waveform = self.load_wav_buffer("../data/audio/AKWF_altosax_0001.wav")
        print("Audio initialized!")

        # --- Buttons ---
        # --- I2C MCP23017 Setup ---
        print("Initializing MCPs at addresses 0x20 and 0x21")
        self.i2c = board.STEMMA_I2C()
        self.mcp1 = MCP23017(self.i2c, address=0x20)
        self.mcp2 = MCP23017(self.i2c, address=0x21)

        self.onboard_buttons = [btn for btn in Buttons.ALL if btn.hw_source == ButtonHardwareSource.ONBOARD]
        self.mcp1_buttons = [btn for btn in Buttons.ALL if btn.hw_source == ButtonHardwareSource.MCP1]
        self.mcp2_buttons = [btn for btn in Buttons.ALL if btn.hw_source == ButtonHardwareSource.MCP2]

        # Configure all 16 pins on each MCP as input + pullup so calibration can
        # remap to any pin without re-init, and unmapped pins still read clean.
        for mcp in (self.mcp1, self.mcp2):
            for pin_num in range(16):
                pin = mcp.get_pin(pin_num)
                pin.direction = digitalio.Direction.INPUT
                pin.pull = digitalio.Pull.UP
        print("Initialized MCPs")

        # initialize the pins for buttons managed by onboard GPIO
        print("Initializing Onboard GPIO")
        onboard_pins = tuple(btn.hw_pin for btn in self.onboard_buttons)
        # keypad library manages our onboard_pins
        self.onboard_button_keys = keypad.Keys(onboard_pins, value_when_pressed=False, pull=True)
        print("Initialized onboard GPIO")

        # 8. Initialize the breath sensor
        self.breath_sensor = BreathSensor(self.i2c)

    async def start_hardware(self):
        await self.breath_sensor.start()

    async def stop_note(self):
        """Releases all active notes and waits for the sound to fade out completely."""
        self.synth.release_all()
        # Wait for the duration of the release envelope to ensure
        # the sound has fully stopped before proceeding.
        await asyncio.sleep(self.NOTE_RELEASE_TIME)


    def play_note(self, midi_number):
        """Converts a MIDI integer to Hertz and plays it with the sax waveform."""
        freq = 440.0 * (2.0 ** ((midi_number - 69) / 12))
        note = synthio.Note(
            frequency=freq,
            envelope=self.sax_envelope,
            waveform=self.sax_waveform
        )
        self.synth.press(note)

    def play_note_if_breathing(self, midi_number):
        if self.breath_sensor.breath_sensor_triggered:
            self.play_note(midi_number)

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
        mcp_register = self.mcp1.gpio
        for btn in self.mcp1_buttons:
            # If the bit is 0, it is pulled to ground (pressed)
            btn.is_pressed = not (mcp_register & (1 << btn.hw_pin))
        mcp_register = self.mcp2.gpio
        for btn in self.mcp2_buttons:
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