
import numpy as np

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

MODULE_NAME = "TuxedoKeyboard"

class TuxedoKeyboard:
    def __init__(self, core):
        self.core = core
        self.gamma = (0.55, 0.48, 0.43)

        # init qt gui
        menu = core.get_tray_menu()
        app = core.get_application()
        self.init_gui(menu, app)

        # register callbacks
        self.core.add_event_callback(MODULE_NAME, "resume",       self.on_resume)
        self.core.add_event_callback(MODULE_NAME, "suspend",      self.on_suspend)
        self.core.add_event_callback(MODULE_NAME, "lid_opened",   self.on_lid_opened)
        self.core.add_event_callback(MODULE_NAME, "lid_closed",   self.on_lid_closed)
        self.core.add_event_callback(MODULE_NAME, "on_ac",        self.on_ac)
        self.core.add_event_callback(MODULE_NAME, "on_battery",   self.on_battery)

    def on_resume(self, event):
        pass

    def on_suspend(self, event):
        pass

    def on_lid_opened(self, event):
        pass

    def on_lid_closed(self, event):
        pass

    def on_ac(self, event):
        pass

    def on_battery(self, event):
        pass

    def init_gui(self, menu, app):
        self.lb = QMenu("LightBar")
        self.lb_ac0 = QAction("Turn Off");      self.lb_ac0.triggered.connect(lambda: self.apply_lightbar_color( (0.0,  0.0,  0.0)) );           self.lb.addAction(self.lb_ac0)
        self.lb_ac1 = QAction("Animation");     self.lb_ac1.triggered.connect(lambda: self.apply_lightbar_animation(1) );                        self.lb.addAction(self.lb_ac1)
        self.lb_ac2 = QAction("White");         self.lb_ac2.triggered.connect(lambda: self.apply_lightbar_color( (1.0,  1.0,  1.0)) );           self.lb.addAction(self.lb_ac2)
        self.lb_ac3 = QAction("Red");           self.lb_ac3.triggered.connect(lambda: self.apply_lightbar_color( (1.0,    0,    0)) );           self.lb.addAction(self.lb_ac3)
        self.lb_ac4 = QAction("Green");         self.lb_ac4.triggered.connect(lambda: self.apply_lightbar_color( (  0,  1.0,    0)) );           self.lb.addAction(self.lb_ac4)
        self.lb_ac5 = QAction("Blue");          self.lb_ac5.triggered.connect(lambda: self.apply_lightbar_color( (  0,    0,  1.0)) );           self.lb.addAction(self.lb_ac5)
        self.lb_ac6 = QAction("Pick a color");  self.lb_ac6.triggered.connect(lambda: self.apply_lightbar_color( self.mono_color_picker()) );    self.lb.addAction(self.lb_ac6)
        menu.addMenu(self.lb)

    def save_state(self, state):
        pass # todo

    def get_state(self):
        return None # todo

    def color_to_voltage(self, color):
        return np.power(color, 1./np.array(self.gamma))

    def mono_color_picker(self):
        color = QColorDialog.getColor().getRgb()
        return (color[0]/255, color[1]/255, color[2]/255)

    def apply_lightbar_color(self, color):
        self.apply_lightbar_voltage(self.color_to_voltage(color))

    def apply_lightbar_voltage(self, voltage):
        with open('/sys/class/leds/lightbar_rgb:1:status/brightness', 'w') as f:
            f.write(str(int(voltage[0]*36)))
        with open('/sys/class/leds/lightbar_rgb:2:status/brightness', 'w') as f:
            f.write(str(int(voltage[1]*36)))
        with open('/sys/class/leds/lightbar_rgb:3:status/brightness', 'w') as f:
            f.write(str(int(voltage[2]*36)))

    def apply_lightbar_animation(self, value):
        with open('/sys/class/leds/lightbar_animation::status/brightness', 'w') as f:
            f.write(str(int(value)))