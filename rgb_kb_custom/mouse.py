
import numpy as np #check_import
import cv2 #check_import
import matplotlib.pyplot as plt #check_import
from pynput.mouse import Controller #DISABLED_check_import

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.idx = np.indices((self.arr.shape[0], self.arr.shape[1]), dtype=self.arr.dtype)
        self.driver = driver
        self.mouse = Controller()
        self.old_pos = None
        self.color_phase = np.random.random() * np.pi * 2

        # parameters:
        self.cm = plt.get_cmap('hsv')

    def update(self):
        sigma = 0.65

        # exponential weight decay
        decay_rate = 0.2 # https://en.wikipedia.org/wiki/Moving_average#Exponentially_weighted_moving_variance_and_standard_deviation
        self.arr = (1-decay_rate)*self.arr

        # shift color phase
        self.color_phase += 0.005

        x, y = self.get_scaled_mouse_pos()

        # dont compute if mouse didnt move
        if self.old_pos is None:
            self.old_pos = (x, y)
        if self.old_pos[0] == x and self.old_pos[1] == y:
            return self.arr

        movement_angle = np.arctan2(self.old_pos[1] - y, self.old_pos[0] - x) + np.pi # 0 to 2*pi
        movement_angle = (movement_angle+self.color_phase) % (np.pi*2)

        length = np.sqrt( (self.old_pos[0]-x)**2 + (self.old_pos[1]-y)**2 ) * 20 # set this last constant so that there will be no empty space between gaussian trails
        diff_x = x - self.old_pos[0]
        diff_y = y - self.old_pos[1]
        gaussian_d = []

        for l in np.linspace(0, length, num=int(length)+1) / length:
            y_kb = (self.old_pos[1] + diff_y*l) * (self.arr.shape[0]-1)
            x_kb = (self.old_pos[0] + diff_x*l) * (self.arr.shape[1]-1)
            gaussian_d.append( np.exp(-0.5 * ((self.idx[0] - y_kb)**2 + (self.idx[1] - x_kb)**2) / sigma**2) )
        gaussian_d = np.array(gaussian_d).reshape((len(gaussian_d), -1))
        gaussian_d = np.max(gaussian_d, axis=0)
        gaussian_d = gaussian_d.reshape((self.arr.shape[0], self.arr.shape[1]))

        gaussian_d = 2 * gaussian_d / np.max(gaussian_d)
        gaussian_d = np.clip(0, 1, gaussian_d*1.0)
        
        color = np.array(self.cm(movement_angle/(2*np.pi))[:-1])
        new_arr = np.expand_dims(gaussian_d, axis=2) * color.reshape(1, 1, -1)
        self.arr += decay_rate * new_arr
        self.arr = np.max(np.stack([self.arr, new_arr]), axis=0)

        self.old_pos = (x, y)
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
        return 15

    def is_enabled(self):
        return True

    def on_exit(self):
        pass
