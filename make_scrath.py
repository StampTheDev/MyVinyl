import math
import random
import struct
import wave
from pathlib import Path

RATE = 48000
DURATION = 0.25

# Start low. Scratch noise can sound much louder than music.
VOLUME = 0.08

output_path = Path("assets/sfx/record_scratch.wav")
output_path.parent.mkdir(parents=True, exist_ok=True)

samples = int(RATE * DURATION)

phase = 0
previous_noise = 0

with wave.open(str(output_path), "w") as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(RATE)

    for i in range(samples):
        t = i / RATE
        progress = i / samples

        # Quick attack and release
        envelope = math.sin(math.pi * progress) ** 0.6

        # Frequency slides downward like a record being dragged
        frequency = 2200 - (1700 * progress)

        phase += 2 * math.pi * frequency / RATE
        tone = math.sin(phase)

        # Rough broadband scraping noise
        noise = random.uniform(-1, 1)

        # Emphasize rapid changes in the noise
        scratch_noise = noise - previous_noise
        previous_noise = noise

        # Slight pulsing gives it a "groove" texture
        groove = 0.65 + 0.35 * abs(
            math.sin(2 * math.pi * 35 * t)
        )

        signal = (
            0.70 * scratch_noise
            + 0.30 * tone
        )

        signal *= envelope
        signal *= groove
        signal *= VOLUME

        sample = int(max(-1, min(1, signal)) * 32767)

        wav.writeframesraw(
            struct.pack("<hh", sample, sample)
        )

print(f"Created {output_path}")
