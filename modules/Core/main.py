
import threading
import queue
import traceback
import signal
import sys
import time
import os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .events import Events

class Core():
    def __init__(self):
        self.project_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')
        self.modules = {}
        self.threads = {}
        self.queues = {}
        self.event_connections = {}

        # init event handlers
        self.core_event_queue = queue.Queue()
        self.core_event_thread = threading.Thread(target=self._core_thread_function, daemon=True).start()
        self._init_module(Events, "Events") # this includes sigint signal exceptionally

        # init gui
        self.app = QApplication([])
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(self.project_path + "/icon.png"))
        self.tray.setVisible(True)
        self.menu = QMenu()
        self.tray.setContextMenu(self.menu)
        QApplication.setQuitOnLastWindowClosed(False)

        # todo
        self.test_thread = threading.Thread(target=self.test_handler, daemon=True).start()
    def test_handler(self):
        import time
        time.sleep(5)

    def add_event_callback(self, module_name, event_name, function):
        self.event_connections[module_name][event_name] = function

    def exit_app(self):
        self.core_event_queue.put({"name": "exit"})

    def exit_app_ask_confirmation(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Are you sure to exit?")
        msgBox.setWindowTitle("System Tray Extensions (STE)")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            self.exit_app()

    def restart_app(self):
        raise NotImplementedError # todo

    def get_tray_menu(self):
        return self.menu

    def get_application(self):
        return self.app

    ###########################################################################

    def _init_module(self, module_class, module_name):
        if module_name in self.modules:
            raise Exception("Module {} is already loaded".format(module_name))

        self.event_connections[module_name] = {}
        self.queues[module_name] = queue.Queue()
        self.threads[module_name] = threading.Thread(target=self._module_thread_function, daemon=True, args=(module_name,)).start()
        self.modules[module_name] = module_class(self)

    def _keep_main_thread(self):
        try:
            self._quit_action = QAction("Quit")
            self._quit_action.triggered.connect(self.exit_app_ask_confirmation)
            self.menu.addAction(self._quit_action)
            self.app.exec_()
        except KeyboardInterrupt:
            print("Qt interrupted by SIGINT")
            sys.exit(0)

    # Module event threading
    def _module_thread_function(self, module_name):
        while True:
            event = self.queues[module_name].get() # blocks the thread
            if event["name"] in self.event_connections[module_name]:
                try:
                    self.event_connections[module_name][event["name"]](event)
                except Exception as e:
                    print(traceback.print_exc())
            self.queues[module_name].task_done() # this may not be needed

    # Main event threading (may not be the main thread)
    def _core_thread_function(self):
        while True:
            event = self.core_event_queue.get() # blocks the thread
            for module_name, queue in self.queues.items():
                # todo check if needed to add?
                queue.put(event)

            if event["name"] == "exit":
                self.exit_thread = threading.Thread(target=self._exit_handler, daemon=True).start()

            self.core_event_queue.task_done()

    def _exit_handler(self):
        self.core_event_queue.join()
        for module_name, queue in self.queues.items():
            print("Waiting for {}".format(module_name))
            queue.join() # todo: timeout
        print("Waiting for Qt")
        self.app.exit()
        sys.exit(0)