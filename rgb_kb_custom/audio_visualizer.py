
# ref:
# - https://python-sounddevice.readthedocs.io/en/0.4.3/examples.html#real-time-text-mode-spectrogram
# - https://soundcard.readthedocs.io/en/latest/

import soundcard as sc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy import signal
import math
import cv2
import time
import struct

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.driver = driver
        self.mics = sc.all_microphones(include_loopback=True)

        self.chunk_history = None

        self.samplerate = 44100
        self.numframes = self.samplerate//15

        # parameters:
        self.cm = plt.get_cmap('jet')

    def process_audio(self, chunk, n_bins=18):
        ########################################
        ######### TODO #########################
        ########################################
        # Process audio chunk and return an array with shape (n_bins,) with values between 0 and 1

        #freqs = np.fft.fftfreq(len(chunk_fft), d=1./self.samplerate)[1:] / self.samplerate

        if self.chunk_history is None:
            self.chunk_history = [chunk]
        else:
            self.chunk_history.insert(0, chunk)
            self.chunk_history = self.chunk_history[:2]
            chunk = np.stack(self.chunk_history)

        chunk = chunk.flatten()
        chunk_fft = np.fft.rfft(chunk)

        chunk_fft_abs = np.absolute(chunk_fft)
        diff = chunk_fft_abs[0]
        chunk_fft_abs = chunk_fft_abs[1:n_bins*10+1]

        chunk_fft_abs = np.median(chunk_fft_abs.reshape(n_bins, 10), axis=1)
        out = (chunk_fft_abs/150)*6
        #out = np.log10(chunk_fft_abs+10)-1

        out = np.clip(out, 0, 6)

        #plt.cla()
        #plt.ylim(0, 200.0)
        #plt.plot(chunk_fft_abs, linewidth=1)
        #plt.bar(range(n_bins), chunk_fft_abs, width=.9)
        #plt.pause(0.001)

        #arr = np.linspace(0, 1, n_bins)
        return out

    def compute_column(self, val, n_rows=6):
        magnitude_hue = []
        for i in range(n_rows):
            magnitude_hue.append( matplotlib.colors.rgb_to_hsv(self.cm(1-i/n_rows)[:-1]) )
        magnitude_hue = np.array(magnitude_hue)

        new_column = np.zeros((self.arr.shape[0], 1)) # (6,1)
        full_keys = int(val * len(new_column))
        last_key_val = val * len(new_column) - full_keys
        new_column[len(new_column)-full_keys:] = 1.0
        if full_keys < len(new_column):
            new_column[len(new_column)-full_keys-1] = last_key_val

        # construct hsv img
        hue = np.ones(new_column.shape) * 360 * magnitude_hue[:,0].reshape(-1,1)
        saturation = np.ones(new_column.shape) * magnitude_hue[:,1].reshape(-1,1)
        value = new_column

        # hsv to rgb
        hsv = np.moveaxis(np.stack([hue, saturation, value]), 0, 2)
        hsv = np.asarray(hsv, dtype=np.float32)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB).squeeze(1)

    def update(self):
        for m in self.mics:
            if m.isloopback:
                print("Found loopback:", m.name)
                if sc.default_speaker().name in m.name:
                    print("soundcard connected to ", m.name)
                    # On Linux, channel -1 is the mono mix of all channels. Remove channel entry for stereo
                    with m.recorder(samplerate=self.samplerate, channels=[-1]) as mic:
                        while self.is_enabled() and self.driver.py_script_thread_enable:
                            data = mic.record(numframes=self.numframes)
                            n_rows = self.arr.shape[0]
                            n_cols = self.arr.shape[1]
                            magnitude = self.process_audio(data, n_cols)

                            for c in range(18):
                                self.arr[:,c,:] = self.compute_column(magnitude[c], n_rows)

                            self.driver.apply_colormap(self.arr)
                            #time.sleep(1/self.get_fps())

        return self.arr

    def get_fps(self):
        return 25

    def is_enabled(self):
        return True

    def on_exit(self):
        pass
