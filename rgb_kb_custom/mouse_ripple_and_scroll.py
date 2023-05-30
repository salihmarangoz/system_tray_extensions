import sys #check_import
import os #check_import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random #check_import
import numpy as np #check_import
import matplotlib.pyplot as plt #check_import
from pynput.mouse import Controller, Listener #DISABLED_check_import
from collections import deque #check_import
from reactive_keyboard_colorful import Ripple #DISABLED_check_import
from mouse_ripple import Circle #DISABLED_check_import

class Shift:
    def __init__(self, arr_shape):
        self.arr_shape = arr_shape
        self.bc_shape = (self.arr_shape[0]*4, self.arr_shape[1]*3, 3)
        self.smoothing_amount = 3
        self.smoothing = 0
        self.is_updated = False  # background roll speed limiter

        # exponential weight decay
        self.decay_rate = 0.15 # https://en.wikipedia.org/wiki/Moving_average#Exponentially_weighted_moving_variance_and_standard_deviation
        self.current_value = 0.0

        self.background = np.zeros(self.bc_shape)
        #np.random.seed(42)
        for i in range(256):
            x = np.random.random()*0.9 + 0.05
            y = np.random.random()*0.9 + 0.05
            color_phase = np.random.random() * np.pi * 2
            c = Circle(x+0.0001, y+0.0001, (x,y), color_phase, self.bc_shape)
            self.background += c.step()
            self.background = np.roll(self.background, shift=1, axis=1)
            self.background = np.roll(self.background, shift=1, axis=0)
        self.background = np.clip(self.background, 0.0, 1.0)

    def register_movement(self, x, y, dx, dy):
        if not self.is_updated:
            return
        self.background = np.roll(self.background, shift=-dx, axis=1)
        self.background = np.roll(self.background, shift=dy, axis=0)
        self.current_value = (1-self.decay_rate)*self.current_value + self.decay_rate*1.0
        self.smoothing = min(self.smoothing+1, self.smoothing_amount)
        self.is_updated = False

    def step(self, arr):
        self.is_updated = True
        if self.smoothing <= 0:
            self.current_value = (1-self.decay_rate)*self.current_value
        self.smoothing = max(self.smoothing-1, 0)
        if self.current_value > 0.01:
            return arr + self.background[:self.arr_shape[0], :self.arr_shape[1]] * self.current_value
        else:
            return arr

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.driver = driver
        self.mouse = Controller()
        self.old_pos = None
        self.color_phase = np.random.random() * np.pi * 2
        self.shift_effect = Shift(arr.shape)
        self.ripple_list = deque()
        self.circle_list = deque()
        self.move_debounce = 0

        # parameters:
        self.cm = plt.get_cmap('hsv')

        listener = Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        listener.start()

    def update(self):
        self.arr = self.arr * 0

        output = None
        for circle in list(self.circle_list):
            if circle.is_visible():
                if output is None:
                    output = circle.step()
                else:
                    new_arr = circle.step()
                    output = np.max(np.stack([output, new_arr]), axis=0)

        if len(self.circle_list) > 0:
            if not self.circle_list[0].is_visible():
                self.circle_list.popleft()

        for ripple in list(self.ripple_list):
            if ripple.is_visible():
                if output is None:
                    output = ripple.step()
                else:
                    output += ripple.step()

        if len(self.ripple_list) > 0:
            if not self.ripple_list[0].is_visible():
                self.ripple_list.popleft()

        if output is not None:
            output = np.clip(output, 0.0, 1.0)
            output = np.where(output < 0.1, 0.1, output) # Keep a minimum backlight
            output = self.shift_effect.step(output)
            self.arr[:,:,:] = output
        else:
            self.arr = self.shift_effect.step(self.arr)
            self.arr = np.where(self.arr < 0.1, 0.1, self.arr) # Keep a minimum backlight

        if self.move_debounce > 0:
            self.move_debounce -= 1

        return self.arr
    
    def on_move(self, x, y):   
        if self.move_debounce == 0:
            x_scaled, y_scaled = self.get_scaled_mouse_pos(x,y)
            if self.old_pos is None:
                self.old_pos = (x_scaled, y_scaled)
            
            # shift color phase
            self.color_phase += 0.005
            if self.color_phase > np.pi*2: self.color_phase = 0

            if not(self.old_pos[0] == x_scaled and self.old_pos[1] == y_scaled):
                self.circle_list.append( Circle(x_scaled, y_scaled, self.old_pos, self.color_phase, self.arr.shape) )
                self.old_pos = (x_scaled, y_scaled)

            self.move_debounce += 1


    def on_click(self, x, y, button, pressed):
        if pressed:
            i_kb, j_kb = self.get_kb_mouse_pos(x,y)
            self.ripple_list.append( Ripple(i_kb, j_kb, self.arr.shape, random.random(), random.random()) )

    def on_scroll(self, x, y, dx, dy):
        self.shift_effect.register_movement(x, y, dx, dy)

    def get_scaled_mouse_pos(self, x, y):
        geometry = self.mouse._display.screen()['root'].get_geometry()._data # some quick dirty hacks. works for xorg
        screen_width = geometry['width']
        screen_height = geometry['height']
        mouse_width = x
        mouse_height = y
        mouse_x = mouse_width / screen_width
        mouse_y = mouse_height / screen_height
        return mouse_x, mouse_y
    
    def get_kb_mouse_pos(self, x, y):
        geometry = self.mouse._display.screen()['root'].get_geometry()._data # some quick dirty hacks. works for xorg
        screen_width = geometry['width']
        screen_height = geometry['height']
        mouse_width = x
        mouse_height = y
        mouse_x = mouse_width / screen_width
        mouse_y = mouse_height / screen_height
        i_kb = mouse_y * (self.arr.shape[0]-1)
        j_kb = mouse_x * (self.arr.shape[1]-1)
        return round(i_kb), round(j_kb)


    def get_fps(self):
        return 15

    def is_enabled(self):
        return True

    def on_exit(self):
        pass