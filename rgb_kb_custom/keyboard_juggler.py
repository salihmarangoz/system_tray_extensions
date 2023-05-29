import random
import numpy as np #check_import
import cv2 #check_import
import logging #check_import
import matplotlib.pyplot as plt #check_import

class CustomEffect:
    def __init__(self, arr, driver):
        random.seed(666)
        self.arr = arr * 0
        self.driver = driver
        self.keyboard_mapper = KeyboardMapper(self.keyboard_cb)
        self.curr_i = 0
        self.curr_j = 0
        self.target_i = 0
        self.target_j = 0
        self.speed = 2.0  # parameter!

        # copied from mouse.py without any changes
        self.idx = np.indices((self.arr.shape[0], self.arr.shape[1]), dtype=self.arr.dtype)
        self.color_phase = np.random.random() * np.pi * 2
        self.old_pos = None
        self.cm = plt.get_cmap('hsv')

    def keyboard_cb(self, code, state, position):
        # state=0 (press), state=1 (release), state=2 (hold)
        if position is not None and state == 0:
            self.target_i, self.target_j = position

            # a quick hack to trigger update when the same key is pressed repeatedly and the ball is on the key
            if self.old_pos is not None:
                self.old_pos = (self.old_pos[0]+0.001, self.old_pos[1]+0.001) 

    def get_scaled_mouse_pos(self):
        diff_i = self.target_i - self.curr_i
        diff_j = self.target_j - self.curr_j
        diff = np.sqrt(diff_i**2 + diff_j**2)
        if diff > 0.01:
            self.curr_i += np.clip(self.speed*diff_i/diff, -np.abs(diff_i), np.abs(diff_i))
            self.curr_j += np.clip(self.speed*diff_j/diff, -np.abs(diff_j), np.abs(diff_j))
        return (self.curr_j+0.5)/self.arr.shape[1], (self.curr_i+0.5)/self.arr.shape[0]

    # copied from mouse.py without any changes
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

    def get_fps(self):
        return 15

    def is_enabled(self):
        return True

    def on_exit(self):
        self.keyboard_mapper.exit()


#################################################################################################################



import inputs #check_import
import threading #check_import
import logging #check_import
class KeyboardMapper:
    def __init__(self, callback):
        self.selected_device = None
        self.callback_function = None
        self.is_enabled = True
        self.thread_list = []
        self.spinner = None

        NOKEY = None # There is a led but no key
        # "KEY_ " prefix are removed for default_map and will be added in process_map()
        #  Note: FN key doesnt work with this method
        self.default_map=[#|  0        |  1     |  2     |  3        |  4       |  5     |  6     |  7     |  8     |  9     |  10       |  11        |  12         |  13          |  14         |  15      |  16      |  17         |
                           ["ESC"      , "F1"   , "F2"   , "F3"      , "F4"     , "F5"   , "F6"   , "F7"   , "F8"   , "F9"   , "F10"     , "F11"      , "F12"       , "PAUSE"      , "SYSRQ"     , "DELETE" , "KPMINUS", "KPPLUS"    ], # 0
                           ["GRAVE"    , "1"    , "2"    , "3"       , "4"      , "5"    , "6"    , "7"    , "8"    , "9"    , "0"       , "MINUS"    , "EQUAL"     , None         , "BACKSPACE" , "NUMLOCK", "KPSLASH", "KPASTERISK"], # 1
                           ["TAB"      , None   , "Q"    , "W"       , "E"      , "R"    , "T"    , "Y"    , "U"    , "I"    , "O"       , "P"        , "LEFTBRACE" , "RIGHTBRACE" , "ENTER"     , "KP7"    , "KP8"    , "KP9"       ], # 2
                           ["CAPSLOCK" , None   , "A"    , "S"       , "D"      , "F"    , "G"    , "H"    , "J"    , "K"    , "L"       , "SEMICOLON", "APOSTROPHE", "BACKSLASH"  , NOKEY       , "KP4"    , "KP5"    , "KP6"       ], # 3
                           ["LEFTSHIFT", NOKEY  , "102ND", "Z"       , "X"      , "C"    , "V"    , "B"    , "N"    , "M"    , "COMMA"   , "DOT"      , "SLASH"     , "RIGHTSHIFT" , "UP"        , "KP1"    , "KP2"    , "KP3"       ], # 4
                           ["LEFTCTRL" , None   , None   , "LEFTMETA", "LEFTALT", None   , None   , "SPACE", None   , None   , "RIGHTALT", "COMPOSE"  , "RIGHTCTRL" , "LEFT"       , "DOWN"      , "RIGHT"  , "KP0"    , "KPDOT"     ]  # 5
                         ]
        self.default_map_inv = {}
        self.process_map()

        self.register_callback(callback)

        #self.listen_for_magic_key()  # METHOD-1: LISTEN FOR A SPECIFIC KEYBOARD
        self.listen_all_keyboards()   # METHOD-2: LISTEN ALL KEYBOARDS


    def process_map(self):
        rows = len(self.default_map)
        cols = len(self.default_map[0])
        for i in range(rows):
            for j in range(cols):
                keycode = self.default_map[i][j]
                if keycode is not None:
                    self.default_map_inv["KEY_" + keycode] = (i,j)

    def listen_all_keyboards(self):
        for device in inputs.devices:
            if device.device_type == "kbd":
                logging.info("Listening keyboard device: %s", device.name)
                thread = threading.Thread(target=self.spinner_entrypoint_, args=(device,))
                self.thread_list.append(thread)
                thread.start()

    # Listens all input devices, sets selected_device to which gets left or right ctrl stroke first
    def listen_for_magic_key(self):
        for device in inputs.devices:
            if device.device_type == "kbd":
                thread = threading.Thread(target=self.listen_for_magic_key_entrypoint_, args=(device,))
                self.thread_list.append(thread)
                thread.start()

    def listen_for_magic_key_entrypoint_(self, device):
        logging.info("Listening magic key from device: %s", device, )
        while self.selected_device is None:
            events = device.read()
            if events:
                for event in events:
                    if self.selected_device is None and (event.code == "KEY_LEFTCTRL" or event.code == "KEY_RIGHTCTRL"):
                        logging.info("Magic key (%s) detected from device: %s", event.code, device.name)
                        self.selected_device = device
                        self.spinner = threading.Thread(target=self.spinner_entrypoint_, args=(self.selected_device,))
                        self.spinner.start()

    def spinner_entrypoint_(self, selected_device):
        while self.is_enabled:
            events = selected_device.read()
            if events:
                for event in events:
                    if event.ev_type == "Key":
                        position = None
                        if event.code in self.default_map_inv:
                            position = self.default_map_inv[event.code]
                        self.callback_function(event.code, event.state, position)

    def register_callback(self, callback):
        self.callback_function = callback

    def exit(self):
        self.is_enabled = False

#def event_cb(code, state, position):
#    print(code, state, position)
#keyboard_mapper = KeyboardMapper(event_cb)



#################################################################################################################



"""
# KEY MAPPINGS ARE FOUND WITH STELLARIS 15 GEN3 USING THIS CODE
import numpy as np
class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr
        self.driver = driver
        self.i = 0
        self.j = 15   # SELECT COLUMN HERE
    def update(self):
        self.arr = self.arr * 0
        self.arr[self.i, self.j] = np.array([1.0, 1.0, 1.0])
        self.i = (self.i + 1) % 6
        return self.arr
    def get_fps(self):
        return 1
    def is_enabled(self):
        return True
    def on_exit(self):
        pass
"""