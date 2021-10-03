
import sys
import glob
import os

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
    """RgbKeyboard Base Class"""
    def __init__(self, core):
        self.core = core
        self.layouts_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../assets/rgb_kb_layouts')
        self.gamma = (1., 1., 1.)

    def get_layouts(self, include_default=False):
        layouts = glob.glob(self.layouts_path + '/*.png', recursive=True)
        if not include_default:
            layouts = filter(lambda x: not x.endswith('/default.png'), layouts)
        return list(layouts)

    def save_state(self, state):
        pass

    def get_state(self, state):
        pass

    def set_gamma(self, gamma=(1., 1., 1.)):
        self.gamma = gamma


############################################################################################

from ite8291r3_ctl import ite8291r3

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