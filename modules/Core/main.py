
import threading
import queue
import traceback
import signal
import sys
import time

# Available events:
# sigint

class Core():
    def __init__(self):
        self.modules = {}
        self.threads = {}
        self.queues = {}
        self.event_connections = {}

        signal.signal(signal.SIGINT, self._signal_handler)

        self.core_event_queue = queue.Queue()
        self.core_event_thread = threading.Thread(target=self._core_thread_function, daemon=True).start()

        self.main_thread_queue = queue.Queue()


    def init_module(self, module_class, module_name):
        if module_name in self.modules:
            raise Exception("Module {} is already loaded".format(module_name))

        self.event_connections[module_name] = {}
        self.queues[module_name] = queue.Queue()
        self.threads[module_name] = threading.Thread(target=self._module_thread_function, daemon=True, args=(module_name,)).start()
        self.modules[module_name] = module_class(self)

    def add_callback(self, module_name, event_name, function):
        self.event_connections[module_name][event_name] = function

    def run_on_main_thread(self, function, *args, **kwargs):
        self.main_thread_queue.put((function, args, kwargs))

    ###########################################################################

    # Module event threading
    def _module_thread_function(self, module_name):
        while True:
            event = self.queues[module_name].get() # blocks the thread
            if event["name"] in self.event_connections[module_name]:
                try:
                    self.event_connections[module_name][event["name"]](event)
                except Exception as e:
                    #print(traceback.print_exc())
                    print(e)
            self.queues[module_name].task_done() # this may not be needed

    # Main event threading (may not be the main thread)
    def _core_thread_function(self):
        while True:
            event = self.core_event_queue.get() # blocks the thread
            for module_name, queue in self.queues.items():
                # todo check if needed to add?
                queue.put(event)
            self.core_event_queue.task_done() # this may not be needed

    # Main thread function for some spesifical tasks like GUI
    def _main_thread_function(self):
        while True:
            function, args, kwargs = self.main_thread_queue.get() # blocks the thread
            try:
                function(*args, **kwargs)
            except Exception as e:
                print(traceback.print_exc())
            self.main_thread_queue.task_done() # this may not be needed

    def _signal_handler(self, sig, frame):
        self.core_event_queue.put({"name": "sigint"})
        self.core_event_queue.join()
        for module_name, queue in self.queues.items():
            print("Waiting for {}".format(module_name))
            queue.join() # todo: timeout
        sys.exit(0)