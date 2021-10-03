
import sys
import glob
import os

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

    def get_layouts(self, include_default=False):
        layouts = glob.glob(self.layouts_path + '/*.png', recursive=True)
        if not include_default:
            layouts = filter(lambda x: not x.endswith('/default.png'), layouts)
        return list(layouts)

    def save_state(self, state):
        pass

    def get_state(self, state):
        pass

############################################################################################

from ite8291r3_ctl import ite8291r3

class Ite8291r3Ctl(RgbKeyboardBase):
    def __init__(self, core):
        super().__init__(core)
        self.ite = ite8291r3.get()

        self.core.add_event_callback("RgbKeyboard", "resume", self.on_resume)
        self.core.add_event_callback("RgbKeyboard", "suspend", self.on_suspend)
        self.core.add_event_callback("RgbKeyboard", "lid_opened", self.on_lid_opened)
        self.core.add_event_callback("RgbKeyboard", "lid_closed", self.on_lid_closed)
        self.core.add_event_callback("RgbKeyboard", "on_ac", self.on_ac)
        self.core.add_event_callback("RgbKeyboard", "on_battery", self.on_battery)

    def init_qt(self):
        pass

    def on_resume(self, event):
        self.ite.set_effect( ite8291r3.effects["rainbow"]())

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
