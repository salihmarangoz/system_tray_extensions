
import sys
import glob
import os
import numpy as np
from PIL import Image
from ite8291r3_ctl import ite8291r3
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
        self.brightness = 1.0

    def get_layouts(self, include_default=False):
        layouts = glob.glob(self.layouts_path + '/*.png', recursive=True)
        if not include_default:
            layouts = filter(lambda x: not x.endswith('/default.png'), layouts)
        return list(layouts)

    def save_state(self, state):
        pass

    def get_state(self, state):
        pass

    def set_gamma(self, gamma):
        self.gamma = gamma

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
        self.ite = ite8291r3.get()
        self.ite.set_brightness(50)

        menu = core.get_tray_menu()
        app = core.get_application()
        self.init_gui(menu, app)

        self.core.add_event_callback("RgbKeyboard", "resume",       self.on_resume)
        self.core.add_event_callback("RgbKeyboard", "suspend",      self.on_suspend)
        self.core.add_event_callback("RgbKeyboard", "lid_opened",   self.on_lid_opened)
        self.core.add_event_callback("RgbKeyboard", "lid_closed",   self.on_lid_closed)
        self.core.add_event_callback("RgbKeyboard", "on_ac",        self.on_ac)
        self.core.add_event_callback("RgbKeyboard", "on_battery",   self.on_battery)

        self.mimic_screen_thread = threading.Thread(target=self.mimic_screen, daemon=True).start()

        """
        colormap = self.layout_to_colormap( self.open_layout( self.layouts_path + "/Coding.png") )
        itemap = self.voltmap_to_itemap( self.color_to_voltage(colormap)*self.brightness )
        self.ite.set_key_colors(itemap)
        """

    def mimic_screen(self):
        top_crop=0.0
        sct = mss.mss()
        monitor = sct.monitors[1]
        left = monitor["left"] + int(monitor["width"]*0.01)
        top = int(monitor["height"]*top_crop)
        right = monitor["width"] - int(monitor["width"]*0.01)
        lower = monitor["height"]
        bbox = (left, top, right, lower)
        dim = (18, 6) # (width, height)

        while True:
            img = cv2.cvtColor(np.asarray(sct.grab(bbox)), cv2.COLOR_BGRA2RGB)
            img = cv2.flip(img, 0)
            img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            colormap = img / 255.0 # normalize after c2 operations
            itemap = self.voltmap_to_itemap( self.color_to_voltage(colormap)*self.brightness )
            self.ite.set_key_colors(itemap)
            time.sleep(1/60) # todo: count delays

    def on_resume(self, event):
        self.ite.set_brightness(50)

    def on_suspend(self, event):
        self.ite.set_brightness(0)

    def on_lid_opened(self, event):
        self.ite.set_brightness(50)

    def on_lid_closed(self, event):
        self.ite.set_brightness(0)

    def on_ac(self, event):
        pass

    def on_battery(self, event):
        pass

    def init_gui(self, menu, app):
        # todo: replace this section with full matrix setup
        self.mc = QMenu("Mono Color")
        self.mc_ac1 = QAction("White");    self.mc_ac1.triggered.connect(lambda: self.ite.set_color((255, 255, 255))); self.mc.addAction(self.mc_ac1)
        self.mc_ac2 = QAction("Red");      self.mc_ac2.triggered.connect(lambda: self.ite.set_color((255,   0,   0))); self.mc.addAction(self.mc_ac2)
        self.mc_ac3 = QAction("Orange");   self.mc_ac3.triggered.connect(lambda: self.ite.set_color((255, 28,    0))); self.mc.addAction(self.mc_ac3)
        self.mc_ac4 = QAction("Yellow");   self.mc_ac4.triggered.connect(lambda: self.ite.set_color((255, 119,   0))); self.mc.addAction(self.mc_ac4)
        self.mc_ac5 = QAction("Green");    self.mc_ac5.triggered.connect(lambda: self.ite.set_color((  0, 255,   0))); self.mc.addAction(self.mc_ac5)
        self.mc_ac6 = QAction("Blue");     self.mc_ac6.triggered.connect(lambda: self.ite.set_color((  0,   0, 255))); self.mc.addAction(self.mc_ac6)
        self.mc_ac7 = QAction("Teal");     self.mc_ac7.triggered.connect(lambda: self.ite.set_color((  0, 255, 255))); self.mc.addAction(self.mc_ac7)
        self.mc_ac8 = QAction("Purple");   self.mc_ac8.triggered.connect(lambda: self.ite.set_color((255,   0, 255))); self.mc.addAction(self.mc_ac8)
        menu.addMenu(self.mc)

    def voltmap_to_itemap(self, voltmap):
        itemap = {}
        for i in range(voltmap.shape[0]):
            for j in range(voltmap.shape[1]):
                itemap[(voltmap.shape[0]-i-1,j)] = tuple( np.asarray(voltmap[i,j]*255, dtype=np.uint8) )
        return itemap