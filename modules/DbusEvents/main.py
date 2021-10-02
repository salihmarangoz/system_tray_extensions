
import subprocess
import os
import threading

class DbusEvents:
    def __init__(self, core):
        self.core = core
        dbus_script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dbus_handler.py')
        self.proc = subprocess.Popen(['python', dbus_script_path],stdout=subprocess.PIPE)
        self.stdin_event_thread = threading.Thread(target=self._stdin_thread_function, daemon=True).start()

    def _stdin_thread_function(self):
        for line in iter(self.proc.stdout.readline, ''):
            event = line.decode("utf-8").strip()
            print("DbusEvents:", event)
            self.core.core_event_queue.put({"name": event})