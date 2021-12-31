
import threading #check_import
import queue #check_import
import traceback #check_import
import signal #check_import
import sys #check_import
import time #check_import
import os #check_import
import json #check_import
import copy #check_import
from threading import Lock #check_import
import subprocess #check_import
import logging #check_import

from PyQt5.QtGui import * #check_import
from PyQt5.QtWidgets import * #check_import


class Node():
    """Node class; assigned to each module for accessing events, states, GUI and special application functions
    """
    def __init__(self, module_name, core, state_manager):
        self.core = core
        self.module_name = module_name
        self.state_manager = state_manager

    """Adds event callbacks. Uses the assigned thread for the module.
    Args:
        event_name: Event name as string. Can be "exit", "on_battery", etc. See README.md for more details.
        callback_function: Calls this function when the given event occured. Passes a dictionary which looks like this {name: "<event_name>", ...}
    """
    def add_event_callback(self, event_name, callback_function):
        self.core.add_event_callback(self.module_name, event_name, callback_function)


    """Sends "exit" event to all modules and tries to terminate the app.
    Args:
        ask_confirmation: Opens a message box asking whether user wants to exit or not. Set to True for asking, default value is False.
    Returns:
        Returns False if user chooses not to exit. 
    """
    def exit_app(self, ask_confirmation=False):
        return self.core.exit_app(ask_confirmation)

    """Sends "exit" event to all modules and tries to terminate the app. Returns value 42 and "start.sh" restarts the app afterwards.
    Args:
        ask_confirmation: Opens a message box asking whether user wants to restarts or not. Set to True for asking, default value is False.
    Returns:
        Returns False if user chooses not to restart.
    """
    def restart_app(self, ask_confirmation=False):
        return self.core.restart_app(ask_confirmation)


    """Saves module state to the state json file.
    Args:
        state: Dictionary including related state values to be saved.
        module_name: Updates assigned module's state if None. If a module name is given, updates the given module state.
    """
    def save_state(self, state, module_name=None):
        if module_name is None:
            module_name = self.module_name
        cur_state = self.state_manager.load_state()
        cur_state[module_name] = state
        self.state_manager.save_state(cur_state)


    """Loads module state from the state json file.
    Args:
        module_name: Loads assigned module's state if None. If a module name is given, loads the given module state.
    Returns:
        Dictionary as how it is saved with using save_state function.
    """
    def load_state(self, module_name=None):
        if module_name is None:
            module_name = self.module_name
        cur_state = self.state_manager.load_state()
        if module_name in cur_state:
            return cur_state[module_name]
        else:
            return None


    """See: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QMenu.html
    Returns:
        QMenu object
    """
    def get_tray_menu(self):
        return self.core.menu


    """See: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QApplication.html
    Returns:
        QApplication object
    """
    def get_application(self):
        return self.core.app


    """Returns project root path.
    Returns:
        Folder path as string.
    """
    def get_project_path(self):
        return self.core.project_path


#####################################################################################################################
# CLASSES BELOW THIS LINE HANDLES INTERNAL STUFF AND CAN BE CHANGED ANY TIME. USE "Node" CLASS FOR DEVELOPING MODUES
#####################################################################################################################


class StateManager:
    def __init__(self, filename):
        self.filename = filename
        self.mutex = Lock()

    def load_state(self):
        self.mutex.acquire()
        try:
            if os.path.isfile(self.filename):
                logging.info("State file is found: %s", self.filename)
                with open(self.filename) as json_file:
                    state = json.load(json_file)
            else:
                logging.warn("State file is NOT found: %s", self.filename)
                state = {}
        finally:
            self.mutex.release()
        return state

    def save_state(self, state):
        self.mutex.acquire()
        try:
            logging.info("State file saved: %s", self.filename)
            with open(self.filename, 'w') as outfile:
                #json.dump(state, outfile)
                json.dump(state, outfile, indent=4)
        finally:
            self.mutex.release()


class EventManager:
    def __init__(self, node):
        self.node = node
        self.process_events = True

        # init dbus handler
        self.node.add_event_callback("exit", self._exit_event)
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
            if len(line) == 0:
                logging.error("dbus_handler.py streamed empty line. exiting...")
                break
            event = line.decode("utf-8").strip()
            logging.info("New event: %s", event)
            self.node.core.core_event_queue.put({"name": event})
            if event == "exit":
                break

class Core():
    def __init__(self):
        self.project_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')
        self.nodes = {}
        self.modules = {}
        self.threads = {}
        self.queues = {}
        self.event_connections = {}
        self.exit_code = 0

        # init state manager
        self.state_manager = StateManager(filename=self.project_path + "/state.json")

        # init event manager and extras
        self.core_event_queue = queue.Queue()
        self.core_event_thread = threading.Thread(target=self._core_thread_function, daemon=True).start()
        self._init_module(EventManager, "EventManager") # this module handles the process signals

        # init gui
        self.app = QApplication([])
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(self.project_path + "/icon.png"))
        self.tray.setVisible(True)
        self.menu = QMenu()
        self.tray.setContextMenu(self.menu)
        QApplication.setQuitOnLastWindowClosed(False)

        # todo: for some quick tests
        self.test_thread = threading.Thread(target=self.test_handler, daemon=True).start()
    def test_handler(self):
        import time # todo: why here???
        time.sleep(5)

    def add_event_callback(self, module_name, event_name, function):
        self.event_connections[module_name][event_name] = function

    def exit_app(self, ask_confirmation=False, text="Are you sure to exit?"):
        if ask_confirmation:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText(text)
            msgBox.setWindowTitle("System Tray Extensions (STE)")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            returnValue = msgBox.exec()
            if not returnValue == QMessageBox.Yes:
                return False
        self.core_event_queue.put({"name": "exit"})

    def restart_app(self, ask_confirmation=False):
        self.exit_code = 42
        retval = self.exit_app(ask_confirmation, text="Are you sure to restart?")
        if retval == False:
            self.exit_code = 0
        return retval

    def _init_module(self, module_class, module_name):
        if module_name in self.modules:
            raise Exception("Module {} is already loaded".format(module_name))

        self.event_connections[module_name] = {}
        self.queues[module_name] = queue.Queue()
        self.threads[module_name] = threading.Thread(target=self._module_thread_function, daemon=True, args=(module_name,)).start()
        self.nodes[module_name] = Node(module_name, self, self.state_manager)

        self.modules[module_name] = module_class(self.nodes[module_name])

    def _keep_main_thread(self):
        try:
            self._restart_action = QAction("Restart")
            self._restart_action.triggered.connect(lambda: self.restart_app(ask_confirmation=True))
            self.menu.addAction(self._restart_action)

            self._quit_action = QAction("Quit")
            self._quit_action.triggered.connect(lambda: self.exit_app(ask_confirmation=True))
            self.menu.addAction(self._quit_action)

            self.app.exec_()
        except KeyboardInterrupt:
            logging.warn("Qt interrupted by SIGINT")
            sys.exit(self.exit_code)

    # Module event threading
    def _module_thread_function(self, module_name):
        while True:
            event = self.queues[module_name].get() # blocks the thread
            if event["name"] in self.event_connections[module_name]:
                try:
                    self.event_connections[module_name][event["name"]](event)
                except Exception as e:
                    logging.error("module_name: %s", module_name)
                    logging.error(traceback.print_exc())
            self.queues[module_name].task_done()

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
            logging.info("Waiting for %s", module_name)
            queue.join() # todo: timeout
        logging.info("Waiting for Qt")
        self.app.exit(self.exit_code)

        # somehow sys.exit doesnt work well... 
        if self.exit_code == 42:
            os._exit(self.exit_code)

        sys.exit(self.exit_code)