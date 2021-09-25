
import importlib
import configparser
import os
import traceback

def main():
    settings = read_settings()

    core_name = settings.get('MAIN', 'core_module', fallback='Core')
    core_module = import_module(core_name)
    core_class = getattr(core_module, core_name)
    core = core_class()

    # Init all modules
    for module_name in os.listdir("modules"):
        if core_name == module_name: continue # the core is already initialized!

        try:
            module_class = getattr(import_module(module_name), module_name)
            core.init_module(module_class, module_name)
            print("Initialized {}".format(module_name))
        except Exception as e:
            #print(traceback.print_exc()) # todo debug mode
            print("Error initializing module {}".format(module_name))

    core._main_thread_function() # pass the main thread to the core

def import_module(module_name):
    return importlib.import_module("modules." + module_name.strip() + ".main")

def read_settings(path="settings.ini"):
    settings = configparser.ConfigParser()
    settings.read(path)
    return settings

if __name__ == "__main__":
    main()