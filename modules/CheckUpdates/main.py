
import sys
import os
import time

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class CheckUpdates:

    def __init__(self, core):
        self.core = core

        # init qt gui
        menu = core.get_tray_menu()
        app = core.get_application()
        self.init_gui(menu, app)

    def init_gui(self, menu, app):
        menu.addSeparator()
        self.update_action = QAction("Check Updates")
        self.update_action.triggered.connect(lambda: self.on_update_triggered());
        menu.addAction(self.update_action)
        menu.addSeparator()

    def on_update_triggered(self):
        import webbrowser
        webbrowser.open("https://github.com/salihmarangoz/system_tray_extensions")