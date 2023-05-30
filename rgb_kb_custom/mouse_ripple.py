import sys #check_import
import os #check_import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random #check_import
import numpy as np #check_import
import matplotlib.pyplot as plt #check_import
from pynput.mouse import Controller, Listener #DISABLED_check_import
from collections import deque #check_import
from reactive_keyboard_colorful import Ripple #DISABLED_check_import

class Circle:
    sigma = 0.65
    decay_rate = 0.2 # https://en.wikipedia.org/wiki/Moving_average#Exponentially_weighted_moving_variance_and_standard_deviation
    animation_steps = 0
    cm = plt.get_cmap('hsv')

    def __init__(self, x, y, old_pos, color_phase, arr_shape):
        self.x = x
        self.y = y
        self.old_pos = old_pos
        self.color_phase= color_phase
        self.arr_shape = arr_shape
        self.idx = np.indices((self.arr_shape[0], self.arr_shape[1]))


        movement_angle = np.arctan2(self.old_pos[1] - self.y, self.old_pos[0] - self.x) + np.pi # 0 to 2*pi
        movement_angle = (movement_angle+self.color_phase) % (np.pi*2)

        length = np.sqrt( (self.old_pos[0]-self.x)**2 + (self.old_pos[1]-self.y)**2 ) * 20 # set this last constant so that there will be no empty space between gaussian trails
        diff_x = self.x - self.old_pos[0]
        diff_y = self.y - self.old_pos[1]

        gaussian_d = []

        for l in np.linspace(0, length, num=int(length)+1) / length:
            y_kb = (self.old_pos[1] + diff_y*l) * (self.arr_shape[0]-1)
            x_kb = (self.old_pos[0] + diff_x*l) * (self.arr_shape[1]-1)
            gaussian_d.append( np.exp(-0.5 * ((self.idx[0] - y_kb)**2 + (self.idx[1] - x_kb)**2) / self.sigma**2) )
        gaussian_d = np.array(gaussian_d).reshape((len(gaussian_d), -1))
        gaussian_d = np.max(gaussian_d, axis=0)
        gaussian_d = gaussian_d.reshape((self.arr_shape[0], self.arr_shape[1]))

        gaussian_d = 2 * gaussian_d / np.max(gaussian_d)
        gaussian_d = np.clip(0, 1, gaussian_d*1.0)

        color = np.array(self.cm(movement_angle/(2*np.pi))[:-1])

        self.circle = np.expand_dims(gaussian_d, axis=2) * color.reshape(1, 1, -1)
        self.circle += self.decay_rate * self.circle

    def step(self):
        self.animation_steps += 1
        self.circle = (1-self.decay_rate) * self.circle

        return self.circle
    
    def is_visible(self):
        return self.animation_steps < 60 # magic number :S

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.driver = driver
        self.mouse = Controller()
        self.old_pos = None
        self.color_phase = np.random.random() * np.pi * 2
        self.ripple_list = deque()
        self.circle_list = deque()
        self.scroll_debounce = 0
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
            self.arr[:,:,:] = output
        else:
            self.arr = np.where(self.arr < 0.1, 0.1, self.arr) # Keep a minimum backlight

        if self.scroll_debounce > 0:
            self.scroll_debounce -= 1

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
        if self.scroll_debounce == 0:
            i_kb, j_kb = self.get_kb_mouse_pos(x,y)
            self.ripple_list.append( Ripple(i_kb, j_kb, self.arr.shape, random.random(), random.random()) )
            self.scroll_debounce += self.get_fps()

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
