
import json
import os
import copy
from threading import Lock

class States:
    def __init__(self, filename):
        self.filename = filename
        self.mutex = Lock()

    def load_state(self):
        self.mutex.acquire()
        try:
            if os.path.isfile(self.filename):
                print("State file is found:", self.filename)
                with open(self.filename) as json_file:
                    state = json.load(json_file)
            else:
                print("State file is NOT found:", self.filename)
                state = {}
        finally:
            self.mutex.release()
        return state

    def save_state(self, state):
        self.mutex.acquire()
        try:
            print("State file saved:", self.filename)
            with open(self.filename, 'w') as outfile:
                json.dump(state, outfile)
        finally:
            self.mutex.release()