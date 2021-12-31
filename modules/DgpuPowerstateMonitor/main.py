
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject
import time
import threading
import logging

class DgpuPowerstateMonitor(QObject):

    hide_signal = pyqtSignal()
    show_signal = pyqtSignal()

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.state = node.load_state()
        self.node.add_event_callback("exit", self.on_exit)

        self.old_gpu_power_state = None

        # init qt gui
        self.enable_power_state_check = True
        menu = node.get_tray_menu()
        app = node.get_application()
        self.init_gui(menu, app)

        self.hide_signal.connect(self.tray.hide)
        self.show_signal.connect(self.tray.show)
        self.start_thread()

    def on_exit(self, event):
        self.enable_power_state_check = False
        self.power_state_check_thread.join()

    def start_thread(self):
        self.power_state_check_thread = threading.Thread(target=self.power_state_check_function, daemon=True)
        self.power_state_check_thread.start()

    def init_gui(self, menu, app):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(self.node.get_project_path() + "/modules/DgpuPowerstateMonitor/gpu_on.png"))
        self.menu = QMenu()
        self.tray.setContextMenu(self.menu)
        self.message_action = QAction("Nvidia GPU is ON. If you see this while on battery you may experience short battery times. Stop using GPU and/or enable RTD3 if possible. Click to dismiss."); self.message_action.triggered.connect(lambda: self.dismiss()); self.menu.addAction(self.message_action)

    def dismiss(self):
        self.enable_power_state_check = False
        self.tray.setVisible(False)

    def power_state_check_function(self):
        logging.info("enter power_state_check_function")
        while self.enable_power_state_check:
            with open('/sys/module/nvidia/drivers/pci:nvidia/0000:01:00.0/power_state', 'r', encoding='utf-8') as f: # todo
                out = f.readlines()
                gpu_power_state = out[0].lower().strip()

            with open('/sys/class/power_supply/BAT0/status', 'r', encoding='utf-8') as f:
                out = f.readlines()
                status = out[0].lower().strip()

            if status != "discharging":
                self.hide_signal.emit()
                time.sleep(3) # todo
                continue

            if self.old_gpu_power_state is None:
                self.old_gpu_power_state = gpu_power_state

            if gpu_power_state == "d3cold":
                #self.tray.setVisible(False)
                self.hide_signal.emit()
            else:
                #self.tray.setVisible(True)
                self.show_signal.emit()
            time.sleep(3) # todo
        logging.info("exit power_state_check_function")




