
import os
import subprocess

class BatteryPowerDrawMonitor():

    def __init__(self, node):
        super().__init__()
        self.node = node
        #self.state = node.load_state()
        self.node.add_event_callback("exit", self.on_exit)

        standalone_py_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'standalone_app.py')
        self.proc = subprocess.Popen(['python', standalone_py_path])

    def on_exit(self, event):
        self.proc.kill()