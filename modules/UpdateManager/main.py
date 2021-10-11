
import sys
import os
import time

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import git

class UpdateManager:
    def __init__(self, core):
        self.core = core

        # init qt gui
        menu = core.get_tray_menu()
        app = core.get_application()
        self.init_gui(menu, app)
        self.check_updates()

    def check_updates(self):
        repo = git.Repo(self.core.project_path)
        for remote in repo.remotes:
            remote.fetch()
        output = repo.git.status("-sb")

        if "behind" in output:
            return True
        return False

    def init_gui(self, menu, app):
        update_status = self.check_updates()

        menu.addSeparator()
        if update_status:
            self.update_action = QAction("New Update Available!")
        else:
            self.update_action = QAction("No updates available")
            self.update_action.setEnabled(False)
        self.update_action.triggered.connect(lambda: self.on_update_triggered());
        menu.addAction(self.update_action)
        menu.addSeparator()

    def on_update_triggered(self):
        import webbrowser
        webbrowser.open("https://github.com/salihmarangoz/system_tray_extensions#update")