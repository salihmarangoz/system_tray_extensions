
import numpy as np #check_import
import cv2 #check_import
import mss #check_import

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr
        self.driver = driver

        top_crop=0.0
        self.sct = mss.mss()
        monitor = self.sct.monitors[1]
        left = monitor["left"] + int(monitor["width"]*0.01)
        top = int(monitor["height"]*top_crop)
        right = monitor["width"] - int(monitor["width"]*0.01)
        lower = monitor["height"]
        self.bbox = (left, top, right, lower)

    def update(self):
        dim = (self.arr.shape[1], self.arr.shape[0])
        img = cv2.cvtColor(np.asarray(self.sct.grab(self.bbox)), cv2.COLOR_BGRA2RGB)
        img = cv2.flip(img, 0)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        self.arr = img / 255.0 # normalize after cv2 operations
        return self.arr

    def get_fps(self):
        return 15

    def is_enabled(self):
        return True

    def on_exit(self):
        pass