
import subprocess
import os
import threading

class Events:
    def __init__(self, core):
        self.core = core
        self.process_events = True

        # init dbus handler
        self.core.add_event_callback("Events", "exit", self._exit_event)
        dbus_script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dbus_handler.py')
        self.proc = subprocess.Popen(['python', dbus_script_path],stdout=subprocess.PIPE)
        self.stdin_event_thread = threading.Thread(target=self._dbus_handler, daemon=True).start()

    def _exit_event(self, event):
        self.process_events = False
        self.proc.kill()

    def _dbus_handler(self):
        for line in iter(self.proc.stdout.readline, ''):
            if not self.process_events:
                break
            event = line.decode("utf-8").strip()
            print("New event:", event)
            self.core.core_event_queue.put({"name": event})
            if event == "exit":
                break