import soundcard as sc
import time

# get a list of all speakers:
speakers = sc.all_speakers()
# get the current default speaker on your system:
default_speaker = sc.default_speaker()

# get a list of all microphones:v
mics = sc.all_microphones(include_loopback=True)
# get the current default microphone on your system:
default_mic = mics[4]

for i in range(len(mics)):
    try:
        print(f"{i}: {mics[i].name}")
    except Exception as e:
        print(e)

with default_mic.recorder(samplerate=148000) as mic, \
            default_speaker.player(samplerate=148000) as sp:
    for i in range(1000):
        data = mic.record(numframes=10000)
        print(data)