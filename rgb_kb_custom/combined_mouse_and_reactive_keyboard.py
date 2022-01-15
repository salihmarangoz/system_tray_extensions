
import numpy as np #check_import
import cv2 #check_import
import importlib #check_import
import os #check_import
import logging #check_import

class CustomEffect:
    def __init__(self, arr, driver):
        self.arr = arr * 0
        self.driver = driver

        self.mouse_effect = self.load_effect("mouse.py", arr, driver)
        self.keyboard_effect = self.load_effect("reactive_keyboard.py", arr, driver)

    # load effect file located in the same directory and create CustomEffect objects
    def load_effect(self, effect_file, arr, driver):
        thisfilepath = os.path.dirname(os.path.realpath(__file__))
        spec = importlib.util.spec_from_file_location("module.name", os.path.join(thisfilepath, effect_file))
        selected_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(selected_module)
        custom_effect = selected_module.CustomEffect(arr.copy(), self)
        return custom_effect

    def update(self):
        # update both effects
        arr_mouse = self.mouse_effect.update()
        arr_keyboard = self.keyboard_effect.update()
        return np.clip(arr_mouse + arr_keyboard, 0, 1) # TODO: Blend

    def get_fps(self):
        return 15

    def is_enabled(self):
        return True

    def on_exit(self):
        self.mouse_effect.on_exit()
        self.keyboard_effect.on_exit()
