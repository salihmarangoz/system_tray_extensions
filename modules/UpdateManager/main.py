
import sys
import os
import time
import threading

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import git
import logging

class UpdateManager:
    def __init__(self, node):
        self.node = node

        # init qt gui
        menu = node.get_tray_menu()
        app = node.get_application()
        self.init_gui(menu, app)
        self.check_updates()

    def check_updates(self):
        self.update_action.setText("Checking updates...")
        self.update_action.setEnabled(False)
        self.update_check_thread = threading.Thread(target=self.check_updates_thread, daemon=True).start()

    def check_updates_thread(self):
        repo = git.Repo(self.node.get_project_path())
        for remote in repo.remotes:
            remote.fetch()
        output = repo.git.status("-sb")

        logging.info("UpdateManager fetch and status: %s", output)
        if "behind" in output:
            self.update_action.setText("New update available!")
            self.update_action.setEnabled(True)
        else:
            self.update_action.setText("No updates available")
            self.update_action.setEnabled(False)

    def init_gui(self, menu, app):
        menu.addSeparator()
        self.update_action = QAction("...")
        self.update_action.setEnabled(False)
        self.update_action.triggered.connect(self.on_update_triggered);
        menu.addAction(self.update_action)

    def on_update_triggered(self):
        import webbrowser
        webbrowser.open("https://github.com/salihmarangoz/system_tray_extensions#update")