
import numpy as np #check_import

from PyQt5.QtGui import * #check_import
from PyQt5.QtWidgets import * #check_import

class TuxedoKeyboard:
    def __init__(self, node):
        self.node = node
        self.gamma = (0.55, 0.48, 0.43) # needs to be calibrated
        self.state = node.load_state()

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
        self.apply_lightbar_color( (0.0,  0.0,  0.0), save_state=False)

    def on_lid_opened(self, event):
        self.reload_state()

    def on_lid_closed(self, event):
        self.reload_state()

    def on_ac(self, event):
        self.reload_state()

    def on_battery(self, event):
        self.reload_state()

    def on_exit(self, event):
        self.apply_lightbar_color( (0.0,  0.0,  0.0), save_state=False)

    def reload_state(self):
        if self.state is not None and "lb_mode" in self.state:
            if self.state["lb_mode"] == "mono":
                self.apply_lightbar_color(self.state["value"])
            elif self.state["lb_mode"] == "animation":
                self.apply_lightbar_animation(self.state["value"])
        else:
            # default:
            self.apply_lightbar_animation()

    def init_gui(self, menu, app):
        self.lb = QMenu("LightBar")
        self.lb_ac0 = QAction("Turn Off");      self.lb_ac0.triggered.connect(lambda: self.apply_lightbar_color( (0.0,  0.0,  0.0)) );           self.lb.addAction(self.lb_ac0)
        self.lb_ac1 = QAction("Animation");     self.lb_ac1.triggered.connect(lambda: self.apply_lightbar_animation() );                        self.lb.addAction(self.lb_ac1)
        self.lb_ac2 = QAction("White");         self.lb_ac2.triggered.connect(lambda: self.apply_lightbar_color( (1.0,  1.0,  1.0)) );           self.lb.addAction(self.lb_ac2)
        self.lb_ac3 = QAction("Red");           self.lb_ac3.triggered.connect(lambda: self.apply_lightbar_color( (1.0,    0,    0)) );           self.lb.addAction(self.lb_ac3)
        self.lb_ac4 = QAction("Green");         self.lb_ac4.triggered.connect(lambda: self.apply_lightbar_color( (  0,  1.0,    0)) );           self.lb.addAction(self.lb_ac4)
        self.lb_ac5 = QAction("Blue");          self.lb_ac5.triggered.connect(lambda: self.apply_lightbar_color( (  0,    0,  1.0)) );           self.lb.addAction(self.lb_ac5)
        self.lb_ac6 = QAction("Pick a color");  self.lb_ac6.triggered.connect(lambda: self.apply_lightbar_color( self.mono_color_picker()) );    self.lb.addAction(self.lb_ac6)
        menu.addMenu(self.lb)

    def color_to_voltage(self, color):
        return np.power(color, 1./np.array(self.gamma))

    def mono_color_picker(self):
        color = QColorDialog.getColor().getRgb()
        return (color[0]/255, color[1]/255, color[2]/255)

    def apply_lightbar_color(self, color, save_state=True):
        voltage = self.color_to_voltage(color)
        with open('/sys/class/leds/lightbar_rgb:1:status/brightness', 'w') as f:
            f.write(str(int(voltage[0]*36)))
        with open('/sys/class/leds/lightbar_rgb:2:status/brightness', 'w') as f:
            f.write(str(int(voltage[1]*36)))
        with open('/sys/class/leds/lightbar_rgb:3:status/brightness', 'w') as f:
            f.write(str(int(voltage[2]*36)))

        if save_state:
            self.state = {"lb_mode": "mono", "value": color}
            self.node.save_state(self.state)

    def apply_lightbar_animation(self, value=1, save_state=True):
        with open('/sys/class/leds/lightbar_animation::status/brightness', 'w') as f:
            f.write(str(int(value)))

        if save_state:
            self.state = {"lb_mode": "animation", "value": value}
            self.node.save_state(self.state)