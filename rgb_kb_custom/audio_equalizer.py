import soundcard as sc # https://soundcard.readthedocs.io/en/latest/

mics = sc.all_microphones(include_loopback=True)

for m in mics:
    if m.isloopback:
        with m.recorder(samplerate=48000) as mic:
            for _ in range(100):
                data = mic.record(numframes=1024)
                print(data)
