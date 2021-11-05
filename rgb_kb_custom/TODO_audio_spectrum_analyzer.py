
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

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.driver = driver
        self.mics = sc.all_microphones(include_loopback=True)

        # parameters:
        self.cm = plt.get_cmap('jet')

    def process_audio(self, data, n_bins=18):
        ########################################
        ######### TODO #########################
        ########################################
        # Process audio data and return an array with shape (n_bins,) with values between 0 and 1
        arr = np.linspace(0, 1, n_bins)
        return arr

    def compute_column(self, val, n_rows=6):
        magnitude_hue = matplotlib.colors.rgb_to_hsv(self.cm(val)[:-1])

        new_column = np.zeros((self.arr.shape[0], 1))
        full_keys = int(val * len(new_column))
        last_key_val = val * len(new_column) - full_keys
        new_column[len(new_column)-full_keys:] = 1.0
        if full_keys < len(new_column):
            new_column[len(new_column)-full_keys-1] = last_key_val

        # construct hsv img
        hue = np.ones(new_column.shape) * 360 * magnitude_hue[0]
        saturation = np.ones(new_column.shape) * magnitude_hue[1]
        value = new_column

        # hsv to rgb
        hsv = np.moveaxis(np.stack([hue, saturation, value]), 0, 2)
        hsv = np.asarray(hsv, dtype=np.float32)
        #return matplotlib.colors.hsv_to_rgb(hsv).squeeze(1)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB).squeeze(1)

    def update(self):
        for m in self.mics:
            if m.isloopback:
                # On Linux, channel -1 is the mono mix of all channels. Remove channel entry for stereo
                with m.recorder(samplerate=44100, channels=[-1]) as mic: 
                    while self.is_enabled() and self.driver.py_script_thread_enable:
                        data = mic.record(numframes=2048)
                        n_rows = self.arr.shape[0]
                        n_cols = self.arr.shape[1]
                        magnitude = self.process_audio(data, n_cols)

                        for c in range(18):
                            self.arr[:,c,:] = self.compute_column(magnitude[c], n_rows)

                        self.driver.apply_colormap(self.arr)
                        time.sleep(1/self.get_fps())

        return self.arr

    def get_fps(self):
        return 20

    def is_enabled(self):
        return True

    def on_exit(self):
        pass


keep_running = True



