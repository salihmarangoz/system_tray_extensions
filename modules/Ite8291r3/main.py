
import sys
import glob
import os
import numpy as np
from PIL import Image
from ite8291r3_ctl import ite8291r3
from ite8291r3_ctl.ite8291r3 import effects as ite8291r3_effects
from ite8291r3_ctl.ite8291r3 import colors as ite8291r3_colors
from ite8291r3_ctl.ite8291r3 import effect as ite8291r3_effect_f
from ite8291r3_ctl.ite8291r3 import effect_attrs as ite8291r3_effect_attrs
import usb
import importlib

import cv2
import mss
import time
import threading

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

############################################################################################


ite8291r3_effects["ripple_reactive"] = ite8291r3_effect_f(0x06, {
        "speed":      (ite8291r3_effect_attrs.SPEED, 0),
        "color":      (ite8291r3_effect_attrs.COLOR, ite8291r3_colors.get("random")),
        "reactive":   (ite8291r3_effect_attrs.REACTIVE, 1),
        "save":       (ite8291r3_effect_attrs.SAVE, 0),
    })

ite8291r3_effects["fireworks_reactive"] = ite8291r3_effect_f(0x11, {
        "speed":      (ite8291r3_effect_attrs.SPEED, 2),
        "color":      (ite8291r3_effect_attrs.COLOR, ite8291r3_colors.get("random")),
        "reactive":   (ite8291r3_effect_attrs.REACTIVE, 1),
        "save":       (ite8291r3_effect_attrs.SAVE, 0),
    })

ite8291r3_effects["random_reactive"] = ite8291r3_effect_f(0x04, {
        "speed":      (ite8291r3_effect_attrs.SPEED, 5),
        "color":      (ite8291r3_effect_attrs.COLOR, ite8291r3_colors.get("random")),
        "reactive":   (ite8291r3_effect_attrs.REACTIVE, 1),
        "save":       (ite8291r3_effect_attrs.SAVE, 0),
    })


class Ite8291r3:
    """Ite8291r3 Base Class
    [png or mp4 file] -> layout (0-255) -> colormap (0-1) x brightness (0-1) -> voltmap (0-1) -> [keyboard driver]
    """

    def __init__(self, node):
        self.node = node
        self.layouts_path = os.path.join(self.node.get_project_path(), 'rgb_kb_custom')
        self.gamma = (0.55, 0.48, 0.43)
        self.screen_thread_enable = False
        self.video_thread_enable = False
        self.py_script_thread_enable = False

        # get saved state
        self.state = self.load_state()
        if self.state is None:
            self.state = self.get_default_state()

        # init rgb kb driver
        self.ite = ite8291r3.get()

        # init qt gui
        menu = node.get_tray_menu()
        app = node.get_application()
        self.submenu = QMenu("RGB Keyboard")
        self.init_gui(self.submenu, app)
        menu.addMenu(self.submenu)

        # reload state
        self.reload_state()

        # register callbacks
        self.node.add_event_callback("resume",       self.on_resume)
        self.node.add_event_callback("suspend",      self.on_suspend)
        self.node.add_event_callback("lid_opened",   self.on_lid_opened)
        self.node.add_event_callback("lid_closed",   self.on_lid_closed)
        self.node.add_event_callback("on_ac",        self.on_ac)
        self.node.add_event_callback("on_battery",   self.on_battery)
        self.node.add_event_callback("exit",         self.on_exit)

    def on_resume(self, event):
        self.ite = ite8291r3.get() # take the control over the device
        self.reload_state()

    def on_suspend(self, event):
        self.update_state({"toggle": False}, save_state=False)
        usb.util.dispose_resources(self.ite.channel.dev) # release the device

    def on_lid_opened(self, event):
        self.reload_state()

    def on_lid_closed(self, event):
        self.update_state({"toggle": False}, save_state=False)

    def on_ac(self, event):
        pass

    def on_battery(self, event):
        pass

    def on_exit(self, event):
        self.update_state({"toggle": False}, save_state=False)

    def init_gui(self, menu, app):
        self.br = QMenu("Brightness")
        self.br1 = QAction("10%");         self.br1.triggered.connect(lambda: self.update_state( {"brightness": 0.1} ));    self.br.addAction(self.br1)
        self.br2 = QAction("20%");         self.br2.triggered.connect(lambda: self.update_state( {"brightness": 0.2} ));    self.br.addAction(self.br2)
        self.br3 = QAction("30%");         self.br3.triggered.connect(lambda: self.update_state( {"brightness": 0.3} ));    self.br.addAction(self.br3)
        self.br4 = QAction("40%");         self.br4.triggered.connect(lambda: self.update_state( {"brightness": 0.4} ));    self.br.addAction(self.br4)
        self.br5 = QAction("50%");         self.br5.triggered.connect(lambda: self.update_state( {"brightness": 0.5} ));    self.br.addAction(self.br5)
        self.br6 = QAction("60%");         self.br6.triggered.connect(lambda: self.update_state( {"brightness": 0.6} ));    self.br.addAction(self.br6)
        self.br7 = QAction("70%");         self.br7.triggered.connect(lambda: self.update_state( {"brightness": 0.7} ));    self.br.addAction(self.br7)
        self.br8 = QAction("80%");         self.br8.triggered.connect(lambda: self.update_state( {"brightness": 0.8} ));    self.br.addAction(self.br8)
        self.br9 = QAction("90%");         self.br9.triggered.connect(lambda: self.update_state( {"brightness": 0.9} ));    self.br.addAction(self.br9)
        self.br10 = QAction("100%");       self.br10.triggered.connect(lambda: self.update_state( {"brightness": 1.0} ));   self.br.addAction(self.br10)
        menu.addMenu(self.br)

        self.mc = QMenu("Mono Color")
        self.mc_ac0 = QAction("Black (Turn off)"); self.mc_ac0.triggered.connect(lambda: self.update_state( {"mode": "mono", "value": (0.0,  0.0,  0.0)} ));           self.mc.addAction(self.mc_ac0)
        self.mc_ac1 = QAction("White");         self.mc_ac1.triggered.connect(lambda: self.update_state( {"mode": "mono", "value": (1.0,  1.0,  1.0)} ));           self.mc.addAction(self.mc_ac1)
        self.mc_ac2 = QAction("Red");           self.mc_ac2.triggered.connect(lambda: self.update_state( {"mode": "mono", "value": (1.0,    0,    0)} ));           self.mc.addAction(self.mc_ac2)
        self.mc_ac3 = QAction("Green");         self.mc_ac3.triggered.connect(lambda: self.update_state( {"mode": "mono", "value": (  0,  1.0,    0)} ));           self.mc.addAction(self.mc_ac3)
        self.mc_ac4 = QAction("Blue");          self.mc_ac4.triggered.connect(lambda: self.update_state( {"mode": "mono", "value": (  0,    0,  1.0)} ));           self.mc.addAction(self.mc_ac4)
        self.mc_ac5 = QAction("Pick a color");  self.mc_ac5.triggered.connect(lambda: self.update_state( {"mode": "mono", "value": self.mono_color_picker()} ));    self.mc.addAction(self.mc_ac5)
        menu.addMenu(self.mc)

        self.ef = QMenu("Effects")
        self.ef_ac1 = QAction("Breathing"); self.ef_ac1.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "breathing"} ));   self.ef.addAction(self.ef_ac1)
        self.ef_ac2 = QAction("Wave");      self.ef_ac2.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "wave"} ));        self.ef.addAction(self.ef_ac2)
        self.ef_ac3 = QAction("Random");    self.ef_ac3.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "random"} ));      self.ef.addAction(self.ef_ac3)
        self.ef_ac3 = QAction("Random (Reactive)");    self.ef_ac3.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "random_reactive"} ));      self.ef.addAction(self.ef_ac3)
        self.ef_ac4 = QAction("Rainbow");   self.ef_ac4.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "rainbow"} ));     self.ef.addAction(self.ef_ac4)
        self.ef_ac5 = QAction("Ripple");    self.ef_ac5.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "ripple"} ));      self.ef.addAction(self.ef_ac5)
        self.ef_ac5 = QAction("Ripple (Reactive but buggy)");    self.ef_ac5.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "ripple_reactive"} ));      self.ef.addAction(self.ef_ac5)
        self.ef_ac6 = QAction("Marquee");   self.ef_ac6.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "marquee"} ));     self.ef.addAction(self.ef_ac6)
        self.ef_ac7 = QAction("Raindrop");  self.ef_ac7.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "raindrop"} ));    self.ef.addAction(self.ef_ac7)
        self.ef_ac8 = QAction("Aurora");    self.ef_ac8.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "aurora"} ));      self.ef.addAction(self.ef_ac8)
        self.ef_ac9 = QAction("Fireworks"); self.ef_ac9.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "fireworks"} ));   self.ef.addAction(self.ef_ac9)
        self.ef_ac9 = QAction("Fireworks (Reactive)"); self.ef_ac9.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "fireworks_reactive"} ));   self.ef.addAction(self.ef_ac9)
        self.ef_ac10 = QAction("Reflect Screen (High CPU Usage)");   self.ef_ac10.triggered.connect(lambda: self.update_state( {"mode": "screen"} ));   self.ef.addAction(self.ef_ac10)
        menu.addMenu(self.ef)

        self.cu = QAction("Custom Visual");   self.cu.triggered.connect(lambda: self.update_state( {"mode": "custom", "value": self.custom_file_picker()} )); menu.addAction(self.cu)

    def reload_state(self):
        # todo read from file
        print("Reloading state:", self.state)
        time.sleep(1)
        self.update_state(new_state=self.state)

    def update_state(self, new_state={}, save_state=True):
        if "brightness" in new_state and not "mode" in new_state:
            self.state.update(new_state)
            if self.state["mode"] == "effect":
                self.ite.set_brightness( int(self.state["brightness"] * 50) )
            if self.state["mode"] == "mono":
                self.state["toggle"] = True
                self.update_state(self.state, save_state)
            if self.state["mode"] == "custom" and os.path.splitext(self.state["value"])[1].lower() == ".png":
                self.update_state(self.state, save_state)

        if "mode" in new_state:
            if new_state["mode"] == "mono":
                self.stop_animation_threads()
                self.ite.set_brightness(50) # set internal brightness to maximum. state["brightness"] will handle this feature
                colormap = self.create_default_colormap(cell_value=new_state["value"])
                self.apply_colormap(colormap)

            if new_state["mode"] == "effect":
                self.stop_animation_threads()
                self.ite.set_effect( ite8291r3_effects[new_state["value"]]() )
                print(int(self.state["brightness"] * 50))
                self.ite.set_brightness( int(self.state["brightness"] * 50) )

            if new_state["mode"] == "screen":
                self.stop_animation_threads()
                self.ite.set_brightness(50)
                self.start_screen_thread()

            if new_state["mode"] == "custom":
                if len(new_state["value"]) == 0:
                    return # cancel update_state
                self.stop_animation_threads()
                self.ite.set_brightness(50)
                if os.path.splitext(new_state["value"])[1].lower() == ".png":
                    layout = self.open_layout(new_state["value"])
                    colormap = self.layout_to_colormap(layout)
                    self.apply_colormap(colormap)
                if os.path.splitext(new_state["value"])[1].lower() == ".mp4":
                    self.start_video_thread(new_state["value"])
                if os.path.splitext(new_state["value"])[1].lower() == ".py":
                    self.start_py_script_thread(new_state["value"])

        if "toggle" in new_state:
            if new_state["toggle"] == False:
                self.stop_animation_threads()
                self.ite.turn_off()
                #self.ite.set_brightness(0)
                # self.ite.freeze() # NEVER USE THIS COMMAND

        if "brightness" in new_state:
                self.br.setTitle("Brightness ({}%)".format(int(new_state["brightness"]*100)))
        elif "brightness" in self.state:
                self.br.setTitle("Brightness ({}%)".format(int(self.state["brightness"]*100)))

        if save_state:
            self.state.update(new_state)
            self.save_state(self.state)

    def apply_voltmap(self, voltmap, experimental=True):
        if experimental:
            NUM_ROWS = 6
            NUM_COLS = 21
            ROW_BUFFER_LEN = 3 * NUM_COLS + 2
            ROW_RED_OFFSET   = 1 + 2 * NUM_COLS
            ROW_GREEN_OFFSET = 1 + 1 * NUM_COLS
            ROW_BLUE_OFFSET  = 1 + 0 * NUM_COLS

            arr = np.zeros((NUM_ROWS, ROW_BUFFER_LEN), dtype=np.uint8)
            voltmap_u8 = np.asarray(voltmap*255, dtype=np.uint8)

            arr[:, ROW_RED_OFFSET:ROW_RED_OFFSET+voltmap.shape[1]] = voltmap_u8[:,:,0]
            arr[:, ROW_GREEN_OFFSET:ROW_GREEN_OFFSET+voltmap.shape[1]] = voltmap_u8[:,:,1]
            arr[:, ROW_BLUE_OFFSET:ROW_BLUE_OFFSET+voltmap.shape[1]] = voltmap_u8[:,:,2]

            try:
                self.ite.enable_user_mode()
                for row in range(NUM_ROWS):
                    self.ite._ite8291r3__set_row_index(row)
                    self.ite._ite8291r3__send_data(bytearray(arr[NUM_ROWS-row-1]))
            except usb.core.USBTimeoutError as e:
                print("usb.core.USBTimeoutError occured but trying to recover!")
                usb.util.dispose_resources(self.ite.channel.dev)
                self.ite = ite8291r3.get()
        else:
            itemap = {}
            for i in range(voltmap.shape[0]):
                for j in range(voltmap.shape[1]):
                    itemap[(voltmap.shape[0]-i-1,j)] = tuple( np.asarray(voltmap[i,j]*255, dtype=np.uint8) )
            self.ite.set_key_colors(itemap)

    def get_layouts(self, include_default=False):
        layouts = glob.glob(self.layouts_path + '/*.png', recursive=True)
        if not include_default:
            layouts = filter(lambda x: not x.endswith('/default.png'), layouts)
        return list(layouts)

    def save_state(self, state):
        self.node.save_state(state)

    def load_state(self):
        return self.node.load_state()

    def color_to_voltage(self, color):
        return np.power(color, 1./np.array(self.gamma))

    def create_default_layout(self, cell_width=18, cell_height=6, cell_width_px=20, cell_height_px=20, grid_width_px=5, grid_height_px=5, grid_value=(0.3,0.3,0.3), cell_value=(1.0,1.0,1.0)):
        row = cell_height * cell_height_px + (cell_height + 1) * grid_height_px
        col = cell_width  * cell_width_px  + (cell_width  + 1) * grid_width_px
        img = np.ones((row, col, 3), dtype=np.float) * cell_value

        for i in range(cell_height+1):
            row = i*(cell_height_px+grid_height_px)
            img[row:row+grid_height_px, :] = grid_value

        for j in range(cell_width+1):
            col = j*(cell_width_px+grid_width_px)
            img[:, col:col+grid_width_px] = grid_value

        return img

    def create_default_colormap(self, cell_width=18, cell_height=6, cell_value=(1.0,1.0,1.0)):
        return np.ones((cell_height, cell_width, 3), dtype=np.float) * cell_value

    def layout_to_colormap(self, layout, cell_width=18, cell_height=6, cell_width_px=20, cell_height_px=20, grid_width_px=5, grid_height_px=5):
        colormap = self.create_default_colormap(cell_width, cell_height)
        for i in range(cell_height):
            for j in range(cell_width):
                row = int(i*(cell_height_px+grid_height_px) + 1.5*grid_height_px)
                col = int(j*(cell_width_px+grid_width_px) + 1.5*grid_width_px)
                colormap[i, j, :] = np.array( layout[row, col] )
        return colormap / 255.0

    def save_layout(self, path, img):
        img_ = Image.fromarray(img)
        img_.save(path, "PNG")

    def open_layout(self, path):
        return np.array( Image.open(path) )[:,:,:3]

    def mono_color_picker(self):
        color = QColorDialog.getColor().getRgb()
        return (color[0]/255, color[1]/255, color[2]/255)

    def custom_file_picker(self, extfilter="Custom effect files (*.mp4 *.png *.py)"):
        dlg = QFileDialog()
        dlg.setDirectory(self.layouts_path)
        dlg.setFileMode(QFileDialog.ExistingFile)
        filename = dlg.getOpenFileName(filter=extfilter)[0]
        return filename

    def apply_colormap(self, colormap, brightness=None):
        if brightness is None:
            brightness = self.state["brightness"]
        self.apply_voltmap( self.color_to_voltage(colormap) * brightness )

    def get_default_state(self):
        return {"mode": "mono",
                "value": (0., 1., 0.),
                "brightness": 1.0,
                "toggle": True}

    def stop_animation_threads(self):
        if self.screen_thread_enable:
            self.screen_thread_enable = False
            self.screen_thread.join()
        if self.video_thread_enable:
            self.video_thread_enable = False
            self.video_thread.join()
        if self.py_script_thread_enable:
            self.py_script_thread_enable = False
            self.py_script_thread.join()

    def start_screen_thread(self):
        self.screen_thread_enable = True
        self.screen_thread = threading.Thread(target=self.screen_function, daemon=True)
        self.screen_thread.start()

    def screen_function(self):
        fps = 30
        top_crop=0.0
        sct = mss.mss()
        monitor = sct.monitors[1]
        left = monitor["left"] + int(monitor["width"]*0.01)
        top = int(monitor["height"]*top_crop)
        right = monitor["width"] - int(monitor["width"]*0.01)
        lower = monitor["height"]
        bbox = (left, top, right, lower)
        dim = (18, 6) # (width, height)

        while self.screen_thread_enable:
            img = cv2.cvtColor(np.asarray(sct.grab(bbox)), cv2.COLOR_BGRA2RGB)
            img = cv2.flip(img, 0)
            img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            colormap = img / 255.0 # normalize after cv2 operations
            voltmap = self.color_to_voltage(colormap) * self.state["brightness"] 
            self.apply_voltmap(voltmap)
            time.sleep(1/fps) # todo: count delays

    def start_video_thread(self, video_path):
        self.video_thread_enable = True
        self.video_file = video_path
        self.video_thread = threading.Thread(target=self.video_function, daemon=True)
        self.video_thread.start()

    def video_function(self):
        is_video_loop = False # todo

        print("starting video_function")
        while self.video_thread_enable:
            cap = cv2.VideoCapture(self.video_file)
            # todo: warn user if tries to open a big file

            dim = (18, 6) # (width, height)
            if not cap.isOpened():
                print("Video not found!")
                break

            fps = cap.get(cv2.CAP_PROP_FPS)
            print("Loaded video with fps:", fps)
            enter_animation = True
            self._video_brightness = 0.0

            while self.video_thread_enable:
                ret, frame = cap.read()
                if ret == False:
                    break

                # enter animation
                if enter_animation and not is_video_loop:
                    self._video_brightness += 1/(fps*2)
                    if self._video_brightness >= self.state["brightness"]:
                        enter_animation = False
                        self._video_brightness = self.state["brightness"]
                else:
                    self._video_brightness = self.state["brightness"]

                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if frame.shape[0] != dim[0] and frame.shape[1] != dim[1]:
                    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
                colormap = img / 255.0 # normalize after cv2 operations
                voltmap = self.color_to_voltage(colormap) * self._video_brightness 
                self.apply_voltmap(voltmap)
                time.sleep(1/fps) # todo: count delays

            # exit animation
            while self._video_brightness > 0 and not is_video_loop and self.video_thread_enable:
                self._video_brightness -= 1/(fps*2)
                voltmap = self.color_to_voltage(colormap) * self._video_brightness 
                self.apply_voltmap(voltmap)
                time.sleep(1/fps) # todo: count delays

        print("exiting video_function")

    def start_py_script_thread(self, py_script_path):
        self.py_script_thread_enable = True
        self.py_script_file = py_script_path
        self.py_script_thread = threading.Thread(target=self.py_script_function, daemon=True)
        self.py_script_thread.start()

    def py_script_function(self):
        print("starting py_script_function")

        spec = importlib.util.spec_from_file_location("module.name", self.py_script_file)
        selected_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(selected_module)

        arr = self.create_default_colormap()
        custom_effect = selected_module.CustomEffect(arr, self)

        while custom_effect.is_enabled() and self.py_script_thread_enable:
            arr = custom_effect.update()

            if arr is None:
                pass
            else:
                voltmap = self.color_to_voltage(arr) * self.state["brightness"] 
                self.apply_voltmap(voltmap)

            time.sleep(1/custom_effect.get_fps()) # todo: count delays

        self.py_script_thread_enable = False
        custom_effect.on_exit()
        print("exiting py_script_function")