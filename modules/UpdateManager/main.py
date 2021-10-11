
import sys
import os
import time
import threading

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
        self.update_check_thread = threading.Thread(target=self.check_updates, daemon=True).start()

    def check_updates(self):
        repo = git.Repo(self.core.project_path)
        for remote in repo.remotes:
            remote.fetch()
        output = repo.git.status("-sb")

        print(output)
        if "behind" in output:
            print("update available!!!!")
            self.update_action.setText("New update available!")
            self.update_action.setEnabled(True)
        else:
            self.update_action.setVisible(False)

    def init_gui(self, menu, app):
        menu.addSeparator()
        self.update_action = QAction("Checking updates...")
        self.update_action.setEnabled(False)
        self.update_action.triggered.connect(lambda: self.on_update_triggered());
        menu.addAction(self.update_action)

    def on_update_triggered(self):
        import webbrowser
        webbrowser.open("https://github.com/salihmarangoz/system_tray_extensions#update")