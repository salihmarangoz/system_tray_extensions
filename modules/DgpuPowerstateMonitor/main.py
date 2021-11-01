
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time
import threading

class DgpuPowerstateMonitor:
    def __init__(self, node):
        self.node = node
        self.state = node.load_state()

        self.node.add_event_callback("exit", self.on_exit)

        # init qt gui
        self.enable_power_state_check = True
        menu = node.get_tray_menu()
        app = node.get_application()
        self.init_gui(menu, app)

        self.start_thread()

    def on_exit(self):
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
        self.message_action = QAction("Nvidia GPU is ON. If you see this while on battery you may experience short battery times. Stop using dGPU and/or enable RTD3. Click to dismiss."); self.message_action.triggered.connect(lambda: self.dismiss()); self.menu.addAction(self.message_action)

    def dismiss(self):
        self.enable_power_state_check = False
        self.tray.setVisible(False)

    def power_state_check_function(self):
        while self.enable_power_state_check:
            with open('/sys/module/nvidia/drivers/pci:nvidia/0000:01:00.0/power_state', 'r', encoding='utf-8') as f: # todo
                out = f.readlines()
                gpu_power_state = out[0].lower().strip()

            if gpu_power_state == "d3cold":
                self.tray.setVisible(False)
            else:
                self.tray.setVisible(True)
            time.sleep(3.0) # todo




