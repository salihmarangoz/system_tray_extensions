# STE Core

Manages events, states, configurations, GUI, etc. for assigned modules.

For developing a new module see `Node` class definition in `modules/Core/main.py`

## Main Idea

- STE Core handles module state and configuration file management, events, initialization order of modules, first initialization of Qt and system tray, and many more.

- Each module has single thread for event handling. If a module holds the thread on the callback function, the module becomes unable to process event queue.
- It is a bit tricky to handle dbus signals since dbus and Qt are both holding main thread for themselves. So, in this project `dbus_handler.py` runs on another process and sends events via file stream.

