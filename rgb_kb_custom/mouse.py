


import numpy as np
import cv2
import psutil
import matplotlib.pyplot as plt
import matplotlib
from pynput.mouse import Controller

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.idx = np.indices((self.arr.shape[0], self.arr.shape[1]), dtype=self.arr.dtype)
        self.driver = driver
        self.mouse = Controller()
        self.old_pos = (0,0)

        # parameters:
        self.cm = plt.get_cmap('hsv')
        self.is_bar_plot = True

    def update(self):
        return self.updatev2()

    def updatev1(self):
        self.arr *= 0.9
        x, y = self.get_scaled_mouse_pos()
        y = y * (self.arr.shape[0]-1)
        x = x * (self.arr.shape[1]-1)
        self.arr[round(y), round(x)] = (1.0, 1.0, 1.0)
        return self.arr

    def updatev2(self):
        decay_rate = 0.1
        color_phase = 5

        self.arr = (1-decay_rate)*self.arr
        color = np.array([1.0, 1.0, 1.0])
        sigma = 1

        x, y = self.get_scaled_mouse_pos()
        y = y * (self.arr.shape[0]-1)
        x = x * (self.arr.shape[1]-1)
        movement_angle = np.arctan2(self.old_pos[1] - y, self.old_pos[0] - x) + np.pi # 0 to 2*pi
        movement_angle = (movement_angle+color_phase) % (np.pi*2)
        if self.old_pos[0] == x and self.old_pos[1] == y:
            return self.arr

        self.old_pos = (x, y)

        color = np.array(self.cm(movement_angle/(2*np.pi))[:-1])
        gaussian_d = np.exp(-0.5 * ((self.idx[0] - y)**2 + (self.idx[1] - x)**2) / sigma**2)
        gaussian_d = gaussian_d / np.max(gaussian_d)
        #gaussian_d = np.clip(0, 1, gaussian_d*1.0)
        
        new_arr = np.expand_dims(gaussian_d, axis=2) * color.reshape(1, 1, -1)
        self.arr += decay_rate * new_arr
        self.arr = np.max(np.stack([self.arr, new_arr]), axis=0)
        return self.arr

    def get_scaled_mouse_pos(self):
        geometry = self.mouse._display.screen()['root'].get_geometry()._data # some quick dirty hacks. works for xorg
        screen_width = geometry['width']
        screen_height = geometry['height']
        mouse_width = self.mouse.position[0]
        mouse_height = self.mouse.position[1]
        mouse_x = mouse_width / screen_width
        mouse_y = mouse_height / screen_height
        return mouse_x, mouse_y

    def get_fps(self):
        return 40

    def is_enabled(self):
        return True

    def on_exit(self):
        pass
