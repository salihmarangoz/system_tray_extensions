
import numpy as np #check_import

from PyQt5.QtGui import * #check_import
from PyQt5.QtWidgets import * #check_import

class TuxedoKeyboard:
    def __init__(self, node):
        self.node = node
        self.gamma = (128, 128, 128) # needs to be calibrated
        self.state = node.load_state()
        self.state.setdefault("lb_color", "255 255 255")
        self.state.setdefault("lb_brightness", "50")

        # init qt gui
        menu = node.get_tray_menu()
        app = node.get_application()
        self.init_gui(menu, app)

        # register callbacks
        self.node.add_event_callback("resume",       self.on_resume)
        self.node.add_event_callback("suspend",      self.on_suspend)
        self.node.add_event_callback("lid_opened",   self.on_lid_opened)
        self.node.add_event_callback("lid_closed",   self.on_lid_closed)
        self.node.add_event_callback("on_ac",        self.on_ac)
        self.node.add_event_callback("on_battery",   self.on_battery)
        self.node.add_event_callback("exit",         self.on_exit)

        self.reload_state()

    def on_resume(self, event):
        self.reload_state()

    def on_suspend(self, event):
        self.apply_lightbar_color( (0, 0, 0), save_state=False)

    def on_lid_opened(self, event):
        self.reload_state()

    def on_lid_closed(self, event):
        self.apply_lightbar_color( (0, 0, 0), save_state=False)

    def on_ac(self, event):
        self.reload_state()

    def on_battery(self, event):
        self.reload_state()

    def on_exit(self, event):
        self.apply_lightbar_color( (0, 0, 0), save_state=False)

    def reload_state(self):
        if self.state is not None:
            if "lb_color" in self.state:
                print('lb_color: ' + str(self.state["lb_color"]))
                self.apply_lightbar_color(self.state["lb_color"])
            if "lb_brightness" in self.state:
                print('lb_brightness: ' + self.state["lb_brightness"])
                self.apply_lightbar_animation(self.state["lb_brightness"])
        else:
            # default:
            self.apply_lightbar_animation()

    def init_gui(self, menu, app):
        self.lb = QMenu("LightBar")
        self.lb_ac0 = QAction("Turn Off");      self.lb_ac0.triggered.connect(lambda: self.apply_lightbar_color( (0  ,    0,    0)) );           self.lb.addAction(self.lb_ac0)
        self.lb_ac1 = QAction("White");         self.lb_ac1.triggered.connect(lambda: self.apply_lightbar_color( (255,  255,  255)) );           self.lb.addAction(self.lb_ac1)
        self.lb_ac2 = QAction("Red");           self.lb_ac2.triggered.connect(lambda: self.apply_lightbar_color( (255,    0,    0)) );           self.lb.addAction(self.lb_ac2)
        self.lb_ac3 = QAction("Green");         self.lb_ac3.triggered.connect(lambda: self.apply_lightbar_color( (  0,  255,    0)) );           self.lb.addAction(self.lb_ac3)
        self.lb_ac4 = QAction("Blue");          self.lb_ac4.triggered.connect(lambda: self.apply_lightbar_color( (  0,    0,  255)) );           self.lb.addAction(self.lb_ac4)
        self.lb_ac5 = QAction("Pick a color");  self.lb_ac5.triggered.connect(lambda: self.apply_lightbar_color( self.mono_color_picker()) );    self.lb.addAction(self.lb_ac5)
        
        self.lb_b = QMenu("Brightness")
        lightLevels = [5, 10, 25, 50, 75, 100]
        self.act = list()
        for b in lightLevels:
            act = QAction(str(b) + "%")
            act.triggered.connect(lambda checked=False, value=b: self.apply_lightbar_animation(str(value)))
            self.lb_b.addAction(act)
            self.act.append(act)
        self.lb.addMenu(self.lb_b)
        menu.addMenu(self.lb)

    def mono_color_picker(self):
        color = QColorDialog.getColor().getRgb()
        return (color[0], color[1], color[2])

    def apply_lightbar_color(self, color, save_state=True):
        with open('/sys/class/leds/rgb:lightbar/multi_intensity', 'w') as f:
            f.write(str(int(color[0])) + " " + str(int(color[1])) + " " + str(int(color[2])))
        print('Color: ' + str(int(color[0])) + " " + str(int(color[1])) + " " + str(int(color[2])))
        if save_state:
            self.state["lb_color"] = color
            self.node.save_state(self.state)

    def apply_lightbar_animation(self, value, save_state=True):
        with open('/sys/class/leds/rgb:lightbar/brightness', 'w') as f:
            f.write(str(int(value)))
        print('Brightness: ' + str(value))
        if save_state:
            self.state["lb_brightness"] = value
            self.node.save_state(self.state)
