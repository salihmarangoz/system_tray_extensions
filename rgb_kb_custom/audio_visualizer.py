
# ref:
# - https://python-sounddevice.readthedocs.io/en/0.4.3/examples.html#real-time-text-mode-spectrogram
# - https://soundcard.readthedocs.io/en/latest/

import soundcard as sc #DISABLED_check_import
import numpy as np #check_import
import math #check_import
import cv2 #check_import
import time #check_import
import logging #check_import
import matplotlib.pyplot as plt #check_import
import matplotlib #check_import

# todo: make for loop without using the driver object

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.driver = driver
        self.mics = sc.all_microphones(include_loopback=True)
        self.chunk_history = None
        self.samplerate = 44100
        self.numframes = self.samplerate//self.get_fps()

        # parameters:
        self.cm = plt.get_cmap('jet')

    def process_audio(self, chunk, n_bins=18):
        ########################################
        ######### TODO #########################
        ########################################
        # Process audio chunk and return an array with shape (n_bins,) with values between 0 and 1

        #freqs = np.fft.fftfreq(len(chunk_fft), d=1./self.samplerate)[1:] / self.samplerate

        # Keep history method-1
        keep_history = 2
        if self.chunk_history is None:
            self.chunk_history = [chunk]
        else:
            self.chunk_history.insert(0, chunk)
            self.chunk_history = self.chunk_history[:keep_history]
            chunk = np.stack(self.chunk_history)
        

        # Compute FFT
        chunk = chunk.flatten()
        chunk_fft = np.fft.rfft(chunk)[1:]

        # Keep history method-2
        """
        if self.chunk_history is not None:
            alpha = 0.33
            chunk_fft = self.chunk_history*alpha + chunk_fft*(1-alpha)
        self.chunk_history = chunk_fft
        """

        # Compute magnitute
        chunk_fft_abs = np.log10( np.absolute(chunk_fft) + 0.00001 ) #* np.linspace(1, 10, len(chunk_fft))

        # split into bars via exponential indexing
        idx = np.geomspace(20, len(chunk_fft_abs), num=n_bins).astype(np.int32)
        idx = np.insert(idx, 0, 0)
        bars = []
        for i in range(len(idx)-1):
            bars.append( np.mean(chunk_fft_abs[idx[i]:idx[i+1]]) )

        # bars scale
        bars_base = 2
        bars_scale = 0.5
        bars = np.array(bars) * np.logspace(0, 1, len(bars), base=bars_base)*bars_scale  #* np.linspace(1, 10, len(bars))

        debug=False
        if debug:
            plt.cla()
            plt.ylim(0, 2.0)
            #plt.plot(chunk_fft_abs, linewidth=0.2)
            plt.bar(range(n_bins), bars, width=.9)
            plt.pause(0.001)

        bars = np.clip(bars, 0, 1)
        return bars

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
        process_a_sample_out_of_N = 1 # make this 2 on slower computers
        counter = 0
        no_data = False

        for m in self.mics:
            if m.isloopback:
                logging.info("Found loopback: %s", m.name)
                if sc.default_speaker().name in m.name:
                    logging.info("soundcard connected to: %s", m.name)
                    # On Linux, channel -1 is the mono mix of all channels. Remove channel entry for stereo
                    with m.recorder(samplerate=self.samplerate, channels=[-1]) as mic:
                        while self.is_enabled() and self.driver.py_script_thread_enable:
                            data = mic.record(numframes=self.numframes)

                            # don't process if no audio
                            if np.any(data) == False:
                                if no_data:
                                    continue
                                no_data = True
                                self.chunk_history = None
                            else:
                                no_data = False


                            if counter >= process_a_sample_out_of_N-1:
                                n_rows = self.arr.shape[0]
                                n_cols = self.arr.shape[1]
                                magnitude = self.process_audio(data, n_cols)

                                for c in range(18):
                                    self.arr[:,c,:] = self.compute_column(magnitude[c], n_rows)

                                self.driver.apply_colormap(self.arr)
                                counter = 0
                            else:
                                counter+=1

        return self.arr

    def get_fps(self):
        return 15

    def is_enabled(self):
        return True

    def on_exit(self):
        pass

"""
ce = CustomEffect(0, None)
for m in ce.mics:
    if m.isloopback:
        if sc.default_speaker().name in m.name:
            with m.recorder(samplerate=ce.samplerate, channels=[-1]) as mic:
                while True:
                    data = mic.record(numframes=ce.numframes)
                    ce.process_audio(data, 18)
"""