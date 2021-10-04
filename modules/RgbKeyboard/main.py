
import sys
import glob
import os
import numpy as np
from PIL import Image
from ite8291r3_ctl import ite8291r3
from ite8291r3_ctl.ite8291r3 import effects as ite8291r3_effects

import cv2
import mss
import time
import threading

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class RgbKeyboard:
    """RgbKeyboard Submodule Loader"""
    def __init__(self, core):
        self.core = core
        self.driver_name = "Ite8291r3Ctl" # todo: read from config file
        self.driver_class = getattr(sys.modules[__name__], self.driver_name)
        self.driver_obj = self.driver_class(self.core)

############################################################################################

class RgbKeyboardBase:
    """RgbKeyboard Base Class
    [png file] -> layout (0-255) -> colormap (0-1) x brightness -> voltmap (0-1) -> [keyboard driver]
    """
    def __init__(self, core):
        self.core = core
        self.layouts_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../rgb_kb_layouts')
        self.gamma = (0.6, 0.5, 0.43)

    def get_layouts(self, include_default=False):
        layouts = glob.glob(self.layouts_path + '/*.png', recursive=True)
        if not include_default:
            layouts = filter(lambda x: not x.endswith('/default.png'), layouts)
        return list(layouts)

    def save_state(self, state):
        pass

    def get_state(self):
        return None # todo

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


############################################################################################

class Ite8291r3Ctl(RgbKeyboardBase):
    def __init__(self, core):
        super().__init__(core)

        # init screen flag
        self.screen_thread_enable = False

        # get saved state
        self.state = self.get_state()
        if self.state is None:
            self.state = self.get_default_state()

        # init rgb kb driver and load state
        self.ite = ite8291r3.get()
        self.reload_state()

        # init qt gui
        menu = core.get_tray_menu()
        app = core.get_application()
        self.init_gui(menu, app)

        # register callbacks
        self.core.add_event_callback("RgbKeyboard", "resume",       self.on_resume)
        self.core.add_event_callback("RgbKeyboard", "suspend",      self.on_suspend)
        self.core.add_event_callback("RgbKeyboard", "lid_opened",   self.on_lid_opened)
        self.core.add_event_callback("RgbKeyboard", "lid_closed",   self.on_lid_closed)
        self.core.add_event_callback("RgbKeyboard", "on_ac",        self.on_ac)
        self.core.add_event_callback("RgbKeyboard", "on_battery",   self.on_battery)

    #################################################

    def on_resume(self, event):
        self.reload_state()

    def on_suspend(self, event):
        self.update_state({"toggle": False}, save_state=False)

    def on_lid_opened(self, event):
        self.reload_state()

    def on_lid_closed(self, event):
        self.update_state({"toggle": False}, save_state=False)

    def on_ac(self, event):
        self.reload_state()

    def on_battery(self, event):
        self.update_state({"toggle": False}, save_state=False) # todo

    #################################################

    def reload_state(self):
        time.sleep(1)
        cur_state = self.state.copy()
        self.state = self.get_default_state()
        self.update_state(new_state=cur_state, save_state=False)


    def update_state(self, new_state={}, save_state=True):
        if "mode" in new_state:
            # stop screen thread
            if self.screen_thread_enable:
                self.screen_thread_enable = False
                self.screen_thread.join()

            if new_state["mode"] == "mono":
                self.ite.set_brightness(50) # set internal brightness to maximum. state["brightness"] will handle this feature
                colormap = self.create_default_colormap(cell_value=new_state["value"])
                self.apply_colormap(colormap)
            if new_state["mode"] == "effect":
                self.ite.set_effect( ite8291r3_effects[new_state["value"]]() )
                self.ite.set_brightness( int(self.state["brightness"] * 50) )
            if new_state["mode"] == "screen":
                self.screen_thread_enable = True
                self.screen_thread = threading.Thread(target=self.screen_function, daemon=True)
                self.screen_thread.start()

        if "toggle" in new_state:
            if new_state["toggle"]:
                self.ite.set_brightness(50)
            else:
                # stop screen thread
                if self.screen_thread_enable:
                    self.screen_thread_enable = False
                    self.screen_thread.join()
                self.ite.set_brightness(0)
                # self.ite.freeze() # NEVER USE THIS COMMAND

        if save_state:
            self.state.update(new_state)
            self.save_state(self.state)

    def get_default_state(self):
        return {"mode": "mono",
                "value": (1., 1., 1.),
                "brightness": 1.0,
                "toggle": True}

    def apply_colormap(self, colormap):
        itemap = self.voltmap_to_itemap( self.color_to_voltage(colormap) * self.state["brightness"] )
        self.ite.set_key_colors(itemap)


    #################################################

    def init_gui(self, menu, app):
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
        self.ef_ac10 = QAction("Screen");   self.ef_ac10.triggered.connect(lambda: self.update_state( {"mode": "screen"} ));   self.ef.addAction(self.ef_ac10)
        menu.addMenu(self.ef)

    def mono_color_picker(self):
        color = QColorDialog.getColor().getRgb()
        return (color[0]/255, color[1]/255, color[2]/255)

    def voltmap_to_itemap(self, voltmap):
        itemap = {}
        for i in range(voltmap.shape[0]):
            for j in range(voltmap.shape[1]):
                itemap[(voltmap.shape[0]-i-1,j)] = tuple( np.asarray(voltmap[i,j]*255, dtype=np.uint8) )
        return itemap

    def screen_function(self):
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
            colormap = img / 255.0 # normalize after c2 operations
            itemap = self.voltmap_to_itemap( self.color_to_voltage(colormap) * self.state["brightness"] )
            self.ite.set_key_colors(itemap)
            time.sleep(1/60) # todo: count delays