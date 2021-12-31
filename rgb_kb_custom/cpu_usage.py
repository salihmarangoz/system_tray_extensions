
import numpy as np #check_import
import cv2 #check_import
import psutil #check_import
import matplotlib.pyplot as plt #check_import
import matplotlib #check_import

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.driver = driver

        # parameters:
        self.cm = plt.get_cmap('jet')
        self.is_bar_plot = True

    def update(self):

        # shift to the left
        self.arr[:, :-1, :] = self.arr[:, 1:, :]

        # get cpu usage
        cpu_usage = psutil.cpu_percent() / 100
        cpu_usage_hue = matplotlib.colors.rgb_to_hsv(self.cm(cpu_usage)[:-1])

        # compute column values
        new_column = np.zeros((self.arr.shape[0], 1))
        full_keys = int(cpu_usage * len(new_column))
        last_key_val = cpu_usage * len(new_column) - full_keys
        if self.is_bar_plot:
            new_column[len(new_column)-full_keys:] = 1.0
            if full_keys < len(new_column):
                new_column[len(new_column)-full_keys-1] = last_key_val
        else:
            if full_keys < len(new_column):
                new_column[len(new_column)-full_keys-1] = 1.0
            else:
                new_column[len(new_column)-full_keys] = 1.0

        # construct hsv img
        hue = np.ones(new_column.shape) * 360 * cpu_usage_hue[0]
        saturation = np.ones(new_column.shape) * cpu_usage_hue[1]
        value = new_column

        # hsv to rgb
        hsv = np.moveaxis(np.stack([hue, saturation, value]), 0, 2)
        hsv = np.asarray(hsv, dtype=np.float32)
        self.arr[:, -1, :] = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB).squeeze(1)

        return self.arr

    def get_fps(self):
        return 5

    def is_enabled(self):
        return True

    def on_exit(self):
        pass