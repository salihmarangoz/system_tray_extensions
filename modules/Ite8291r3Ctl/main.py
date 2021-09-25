
from ite8291r3_ctl import ite8291r3

class Ite8291r3Ctl:
    def __init__(self, core):
        self.core = core
        self.ite = ite8291r3.get()

        self.ite.set_effect( ite8291r3.effects["wave"]())

        self.core.add_callback("Ite8291r3Ctl", "sigint", self.custom_event)

        mt = self.core.run_on_main_thread
        mt(self.foobar, text="This is running on the main thread")

    def custom_event(self, event):
        print("custom_event", event)

    def foobar(self, text):
        print(text)

