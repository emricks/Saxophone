import array
import asyncio
import math
import time

import audiocore


class Metronome:
    """A self-driving beat-clock device.

    Construct once with a hardware reference. `start(bpm)` launches an internal
    asyncio task that wakes on each beat boundary and fires a click via the
    mixer. Callers only **read** from the metronome — `pulse_intensity(now)`
    for a decaying 0..1 value to drive a visual, `beat_count` for the
    total beats fired since start, `last_beat_at` for the wall-clock time
    of the most recent beat. Nothing the caller does advances the clock.

    The click sample is generated in-memory at construction (no asset file).
    It's a short damped sine — sounds like a soft tick — matched to the
    SaxHardware mixer's 22050 Hz / 16-bit signed mono format.
    """

    CLICK_VOICE = 1            # accompaniment voice; song mode also uses this
    CLICK_FREQ_HZ = 2000.0
    ACCENT_FREQ_HZ = 2800.0    # downbeat (first beat of each measure)
    CLICK_DURATION_S = 0.03
    CLICK_DECAY_RATE = 120.0   # exponential decay constant; bigger = snappier
    DEFAULT_BEATS_PER_MEASURE = 4

    def __init__(self, hardware, on_beat=None):
        """`on_beat`, if given, is called as `on_beat(beat_time)` immediately
        after each click fires. Use it to drive any beat-synchronous side
        effects (visual pulse, drill advancement, etc.) — anything that needs
        to happen on the beat goes through this hook rather than polling."""
        self.hw = hardware
        self.bpm = 0
        self.beat_interval = 0.0
        self.last_beat_at = None    # monotonic() of the most recent fired beat
        self.beat_count = 0         # total beats fired since the current start()
        self.beats_per_measure = self.DEFAULT_BEATS_PER_MEASURE
        self.on_beat = on_beat
        self._task = None
        self._click_sample = self._make_click_sample(self.CLICK_FREQ_HZ)
        self._accent_sample = self._make_click_sample(self.ACCENT_FREQ_HZ)

    def _make_click_sample(self, frequency_hz):
        sample_rate = 22050
        n = int(sample_rate * self.CLICK_DURATION_S)
        samples = array.array("h")
        amplitude = 0x6FFF  # leave headroom against clipping
        for i in range(n):
            t = i / sample_rate
            envelope = math.exp(-t * self.CLICK_DECAY_RATE)
            value = int(amplitude * envelope * math.sin(2.0 * math.pi * frequency_hz * t))
            samples.append(value)
        try:
            return audiocore.RawSample(samples, sample_rate=sample_rate)
        except Exception as e:
            print(f"Metronome: could not build click sample ({e}); will run silent.")
            return None

    def start(self, bpm, beats_per_measure=None):
        """Begin ticking at the given BPM. Launches the internal task; cancels
        any previous task first. `beats_per_measure` controls how often the
        accent (downbeat) click fires — defaults to 4/4."""
        if bpm <= 0:
            return
        self.stop()
        self.bpm = bpm
        self.beat_interval = 60.0 / bpm
        self.beat_count = 0
        self.last_beat_at = None
        if beats_per_measure is not None and beats_per_measure > 0:
            self.beats_per_measure = beats_per_measure
        self._task = asyncio.create_task(self._run())

    def stop(self):
        if self._task is not None:
            self._task.cancel()
            self._task = None
        self.bpm = 0
        self.beat_interval = 0.0
        try:
            self.hw.mixer.voice[self.CLICK_VOICE].stop()
        except Exception:
            pass

    async def _run(self):
        """Internal beat loop. Fires a beat, sleeps to the next boundary,
        repeats. Schedule (not delays) is what's tracked, so individual sleeps
        being slightly long don't cause cumulative drift."""
        next_beat = time.monotonic()
        try:
            while True:
                delay = next_beat - time.monotonic()
                if delay > 0:
                    await asyncio.sleep(delay)
                self._fire_beat(next_beat)
                next_beat += self.beat_interval
        except asyncio.CancelledError:
            pass

    def _fire_beat(self, beat_time):
        self.last_beat_at = beat_time
        self.beat_count += 1
        # Downbeat = first beat of each measure (beat_count of 1, 5, 9, ... in 4/4).
        is_downbeat = (self.beat_count - 1) % self.beats_per_measure == 0
        sample = self._accent_sample if is_downbeat else self._click_sample
        if sample is None:
            sample = self._click_sample  # fall back if accent failed to build
        if sample is not None:
            try:
                self.hw.mixer.voice[self.CLICK_VOICE].play(sample, loop=False)
            except Exception as e:
                print(f"Metronome click failed: {e}")
        if self.on_beat is not None:
            try:
                self.on_beat(beat_time)
            except Exception as e:
                print(f"Metronome on_beat handler failed: {e}")