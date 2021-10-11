
import sys
import glob
import os
import numpy as np
from PIL import Image
from ite8291r3_ctl import ite8291r3
from ite8291r3_ctl.ite8291r3 import effects as ite8291r3_effects
import usb

import cv2
import mss
import time
import threading

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

MODULE_NAME = "FullRgbKeyboard"

class FullRgbKeyboard:
    """RgbKeyboard Submodule Loader"""
    def __init__(self, core):
        self.core = core
        self.driver_name = "Ite8291r3Ctl" # todo: read from config file
        self.driver_class = getattr(sys.modules[__name__], self.driver_name)
        self.driver_obj = self.driver_class(self.core)

############################################################################################

class FullRgbKeyboardBase:
    """RgbKeyboard Base Class
    [png file] -> layout (0-255) -> colormap (0-1) x brightness (0-1) -> voltmap (0-1) -> [keyboard driver]
    """

    def __init__(self, core):
        self.core = core
        self.layouts_path = os.path.join(self.core.project_path, 'rgb_kb_custom')
        self.gamma = (0.6, 0.5, 0.5)
        self.screen_thread_enable = False
        self.video_thread_enable = False

    def get_layouts(self, include_default=False):
        layouts = glob.glob(self.layouts_path + '/*.png', recursive=True)
        if not include_default:
            layouts = filter(lambda x: not x.endswith('/default.png'), layouts)
        return list(layouts)

    def save_state(self, state):
        self.core.save_state(MODULE_NAME, state)

    def load_state(self):
        return self.core.load_state(MODULE_NAME)

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
        return np.array( Image.open(path) )

    def mono_color_picker(self):
        color = QColorDialog.getColor().getRgb()
        return (color[0]/255, color[1]/255, color[2]/255)

    def custom_file_picker(self, extfilter="Custom effect files (*.mp4 *.png)"):
        dlg = QFileDialog()
        dlg.setDirectory(self.layouts_path)
        dlg.setFileMode(QFileDialog.ExistingFile)
        filename = dlg.getOpenFileName(filter=extfilter)[0]
        return filename

    def apply_voltmap(self, voltmap):
        pass # not implemented

    def apply_colormap(self, colormap):
        self.apply_voltmap( self.color_to_voltage(colormap) * self.state["brightness"] )

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



############################################################################################

class Ite8291r3Ctl(FullRgbKeyboardBase):
    def __init__(self, core):
        super().__init__(core)
        # get saved state
        self.state = self.load_state()
        if self.state is None:
            self.state = self.get_default_state()

        # init rgb kb driver
        self.ite = ite8291r3.get()

        # init qt gui
        menu = core.get_tray_menu()
        app = core.get_application()
        self.init_gui(menu, app)

        # reload state
        self.reload_state()

        # register callbacks
        self.core.add_event_callback(MODULE_NAME, "resume",       self.on_resume)
        self.core.add_event_callback(MODULE_NAME, "suspend",      self.on_suspend)
        self.core.add_event_callback(MODULE_NAME, "lid_opened",   self.on_lid_opened)
        self.core.add_event_callback(MODULE_NAME, "lid_closed",   self.on_lid_closed)
        self.core.add_event_callback(MODULE_NAME, "on_ac",        self.on_ac)
        self.core.add_event_callback(MODULE_NAME, "on_battery",   self.on_battery)
        self.core.add_event_callback(MODULE_NAME, "exit",         self.on_exit)

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
        self.br0 = QAction("Turn Off");    self.br0.triggered.connect(lambda: self.update_state({"toggle": False}, save_state=True));    self.br.addAction(self.br0)
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
        self.ef_ac4 = QAction("Rainbow");   self.ef_ac4.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "rainbow"} ));     self.ef.addAction(self.ef_ac4)
        self.ef_ac5 = QAction("Ripple");    self.ef_ac5.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "ripple"} ));      self.ef.addAction(self.ef_ac5)
        self.ef_ac6 = QAction("Marquee");   self.ef_ac6.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "marquee"} ));     self.ef.addAction(self.ef_ac6)
        self.ef_ac7 = QAction("Raindrop");  self.ef_ac7.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "raindrop"} ));    self.ef.addAction(self.ef_ac7)
        self.ef_ac8 = QAction("Aurora");    self.ef_ac8.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "aurora"} ));      self.ef.addAction(self.ef_ac8)
        self.ef_ac9 = QAction("Fireworks"); self.ef_ac9.triggered.connect(lambda: self.update_state( {"mode": "effect", "value": "fireworks"} ));   self.ef.addAction(self.ef_ac9)
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
                self.start_screen_thread()

            if new_state["mode"] == "custom":
                if len(new_state["value"]) == 0:
                    return # cancel update_state
                self.stop_animation_threads()
                if os.path.splitext(new_state["value"])[1].lower() == ".png":
                    layout = self.open_layout(new_state["value"])
                    colormap = self.layout_to_colormap(layout)
                    self.apply_colormap(colormap)
                if os.path.splitext(new_state["value"])[1].lower() == ".mp4":
                    self.start_video_thread(new_state["value"])

        if "toggle" in new_state:
            if new_state["toggle"] == False:
                self.br.setTitle("Brightness (Turned Off)")
                self.stop_animation_threads()
                self.ite.turn_off()
                # self.ite.set_brightness(0) # turn_off is better...
                # self.ite.freeze() # NEVER USE THIS COMMAND

        if "brightness" in new_state:
                self.br.setTitle("Brightness ({}%)".format(int(new_state["brightness"]*100)))
        elif "brightness" in self.state:
                self.br.setTitle("Brightness ({}%)".format(int(self.state["brightness"]*100)))

        if save_state:
            self.state.update(new_state)
            self.save_state(self.state)


    def voltmap_to_itemap(self, voltmap):
        itemap = {}
        for i in range(voltmap.shape[0]):
            for j in range(voltmap.shape[1]):
                itemap[(voltmap.shape[0]-i-1,j)] = tuple( np.asarray(voltmap[i,j]*255, dtype=np.uint8) )
        return itemap

    def apply_voltmap(self, voltmap):
        self.ite.set_key_colors(self.voltmap_to_itemap(voltmap))