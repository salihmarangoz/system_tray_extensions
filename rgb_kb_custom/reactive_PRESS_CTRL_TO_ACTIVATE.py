
import numpy as np

# todo: some quick tricks to see if keyboard effects work properly and a small demonstration of the effect. currently doesnt support multiple ripple waves

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.driver = driver
        self.keyboard_mapper = KeyboardMapper(self.keyboard_cb)

        self.r = -1
        self.i = 0
        self.j = 0

    def keyboard_cb(self, code, state, position):
        if position is not None:
            i, j = position
            self.i = i
            self.j = j
            self.r = 0

    def update(self):
        self.arr = self.arr * 0
        if self.r >= 0:
            self.r += 0.4
            ii, jj = np.meshgrid(range(self.arr.shape[0]), range(self.arr.shape[1]), indexing='ij')
            ii = ii - self.i
            jj = jj - self.j
            scale = self.r * 3 # ripple wave length
            output = np.exp( -np.abs(ii**2 + jj**2 - self.r**2) / scale )
            #output *= 1 / self.r # decrease wave magnitute over time
            output = output.reshape((self.arr.shape[0], self.arr.shape[1], 1))
            self.arr[:,:,:] = output

        return self.arr

    def get_fps(self):
        return 20

    def is_enabled(self):
        return True

    def on_exit(self):
        pass



#################################################################################################################



import inputs
import threading
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

        self.listen_for_magic_key()
        self.register_callback(callback)

    def process_map(self):
        rows = len(self.default_map)
        cols = len(self.default_map[0])
        for i in range(rows):
            for j in range(cols):
                keycode = self.default_map[i][j]
                if keycode is not None:
                    self.default_map_inv["KEY_" + keycode] = (i,j)

    # Listens all input devices, sets selected_device to which gets left or right ctrl stroke first
    def listen_for_magic_key(self):
        for device in inputs.devices:
            if device.device_type == "kbd":
                thread = threading.Thread(target=self.listen_for_magic_key_entrypoint_, args=(device,))
                self.thread_list.append(thread)
                thread.start()

    def listen_for_magic_key_entrypoint_(self, device):
        print("Listening magic key from device:", device, )
        while self.selected_device is None:
            events = device.read()
            if events:
                for event in events:
                    if self.selected_device is None and (event.code == "KEY_LEFTCTRL" or event.code == "KEY_RIGHTCTRL"):
                        print("Magic key ({}) detected from device: {}".format(event.code, device.name))
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