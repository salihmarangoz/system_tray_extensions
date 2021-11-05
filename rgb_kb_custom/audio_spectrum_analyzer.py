import soundcard as sc # https://soundcard.readthedocs.io/en/latest/
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy import signal
import math
import cv2


class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.driver = driver
        self.mics = sc.all_microphones(include_loopback=True)

        # parameters:
        self.cm = plt.get_cmap('jet')
        self.is_bar_plot = True
        self.gain = 10

        self.high = 2000
        self.low = 100
        self.delta_f = (self.high - self.low) / (self.arr.shape[1] - 1)
        

    def update(self):
        # https://python-sounddevice.readthedocs.io/en/0.4.3/examples.html#real-time-text-mode-spectrogram
        for m in self.mics:
            if m.isloopback:
                with m.recorder(samplerate=44100, channels=[-1]) as mic: # On Linux, channel -1 is the mono mix of all channels. 
                    while self.is_enabled() and self.driver.py_script_thread_enable:
                        data = mic.record(numframes=2048)
                        fftsize = (self.arr.shape[1] - 1) * 2

                        low_bin = math.floor(self.low / self.delta_f)

                        gradient = np.linspace(0, 1, 100)

                        magnitude = np.abs(np.fft.rfft(data[:, 0], n=fftsize))
                        magnitude *= 10 / fftsize
                        line = (gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                                for x in magnitude[low_bin:low_bin + 18])
                        line = np.array(list(line))
                        print(line.shape)

                        print(self.cm(line)[:, :-1].shape)
                        line_hue = matplotlib.colors.rgb_to_hsv(self.cm(line)[:, :-1])

                        print(line_hue.shape)

                        hue = np.ones(18) * 360 * line_hue[:,0]
                        saturation = np.ones(18) * line_hue[:,1]
                        value = line

                        print(hue.shape, saturation.shape, value.shape)

                        hsv = np.moveaxis(np.stack([hue, saturation, value]), 0, 1)
                        hsv = np.asarray(hsv, dtype=np.float32)
                        self.arr[0, :, :] = matplotlib.colors.hsv_to_rgb(hsv)

                        self.driver.apply_colormap(self.arr)



        return self.arr

    def get_fps(self):
        return 20

    def is_enabled(self):
        return True

    def on_exit(self):
        pass


keep_running = True



