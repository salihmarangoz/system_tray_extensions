

class BaseCore:
    def __init__(self, backend_class):
        self.backend = backend_class()
        print("Initialized Core!")
