
import sys #check_import
import os #check_import
import time #check_import
import threading #check_import

from PyQt5.QtGui import * #check_import
from PyQt5.QtWidgets import * #check_import

import git #DISABLED_check_import
import logging #check_import
import webbrowser #check_import

class About:
    def __init__(self, node):
        self.node = node

        # init qt gui
        menu = node.get_tray_menu()
        app = node.get_application()

        #menu.addSeparator()
        self.update_action = QAction("About")
        self.update_action.setEnabled(True)
        self.update_action.triggered.connect(self.on_update_triggered);
        menu.addAction(self.update_action)


    def on_update_triggered(self):
        webbrowser.open("https://github.com/salihmarangoz/system_tray_extensions")