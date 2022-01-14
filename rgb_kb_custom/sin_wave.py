
import numpy as np #check_import
import cv2 #check_import
import logging #check_import

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr
        self.driver = driver
        self.phase = np.random.uniform()*np.pi*2
        self.hue = np.random.uniform()*360

        # parameters
        self.is_psychedelic = np.random.uniform() < 0.02 # easter egg :)
        self.wave_tickness = np.e # 2 for tick and increase value to decrease tickness
        self.wave_width = np.pi*2
        self.phase_increment = 0.2
        self.hue_increment = 1

    def update(self):
        self.arr = self.arr * 0

        # compute sin values and keyboard reference points
        y_ref = np.tile(np.linspace(-1, +1, self.arr.shape[0]).reshape(-1,1), self.arr.shape[1])
        x = np.linspace(0, self.wave_width, self.arr.shape[1])
        y = np.sin(x+self.phase)

        # score higher values for pixels which are closer to keyboard references
        score = np.absolute(y_ref - y)
        score = -score + np.max(score)
        score = self.wave_tickness ** score
        score = score / np.max(score)

        # construct hsv img
        if self.is_psychedelic:
            hue = (score*360 + self.hue) % 360
            saturation = np.ones(score.shape)
            value = np.ones(score.shape)
        else:
            hue = np.ones(score.shape) * self.hue
            saturation = np.ones(score.shape)
            value = score

        # hsv to rgb
        hsv = np.moveaxis(np.stack([hue, saturation, value]), 0, 2)
        hsv = np.asarray(hsv, dtype=np.float32)
        self.arr = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

        self.phase = (self.phase + self.phase_increment) % (np.pi*2)
        self.hue = (self.hue + self.hue_increment) % 360
        return self.arr

    def get_fps(self):
        return 15

    def is_enabled(self):
        return True

    def on_exit(self):
        pass