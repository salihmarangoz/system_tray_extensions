
import importlib
import configparser


def main():
    settings = read_settings()

    core_name = settings.get('MAIN', 'core', fallback='SteCore')
    core_module = import_module(core_name)
    core_class = getattr(core_module, core_name)

    backend_name = settings.get('MAIN', 'backend', fallback='SteQtBackend')
    backend_module = import_module(backend_name)
    backend_class = getattr(backend_module, backend_name)

    core = core_class(backend_class)


def import_module(module_name):
    return importlib.import_module("modules." + module_name.strip() + ".main")

def read_settings(path="settings.ini"):
    settings = configparser.ConfigParser()
    settings.read(path)
    return settings

if __name__ == "__main__":
    main()