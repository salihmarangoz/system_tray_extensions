
import os
import sys
import signal
from pathlib import Path
import numpy as np

from PIL import Image



class SteQtBackend():
    def __init__(self):
        print("Init ste qt backend!")




#################### BASE EXTENSION CLASSES #####################################

class BaseExtension:
    def __init__(self, state, path, settings):
        self.path = path
        self.settings = settings

    def save_state(self, state):
        # TODO
        pass

    def on_add_actions(self, menu):
        raise NotImplementedError

    def on_load_state(self):
        raise NotImplementedError

    def on_battery(self):
        pass

    def on_ac(self):
        pass

    def on_battery_level_change(self, battery_level):
        pass

    def on_presuspend(self):
        pass

    def on_postsuspend(self):
        pass

    def on_prehibernate(self):
        pass

    def on_posthibernate(self):
        pass


class BaseRgbKeyboardExtension(BaseExtension):
    def __init__(self, path, settings):
        super().__init__(path, settings)
        self.gamma_correction = (2.0, 3.0, 7.0) #todo
        # todo layout sizes

    def create_default_layout(self, fill_value=(80,80,80)): # todo size
        img = np.ones((6*20+7*5, 18*20+19*5, 3), dtype=np.uint8)*255

        for i in range(7):
            img[i*25:i*25+5, :] = fill_value

        for j in range(19):
            img[:, j*25:j*25+5] = fill_value

        return img

    def image_to_color_map(self, img):
        color_map = {}
        for i in range(6):
            for j in range(18):
                color_map[(5-i,j)] = tuple(img[i*25+12, j*25+12])
        return color_map

    def save_img(self, path, img):
        img_ = Image.fromarray(img)
        img_.save(path, "PNG")

    def open_img(self, path, correct_gamma=True):
        img_ = Image.open(path)
        img = np.array(img_, dtype=np.float32)[:,:,:3] / 255.0
        if correct_gamma:
            img = img**self.gamma_correction
        img = np.array(img*255, dtype=np.uint8)
        return img


#################### MAIN APP #####################################

class MainApp():
    def __init__(self):
        self.repository_url = "https://github.com/salihmarangoz/ite8291r3-gui"
        self.app_title = "[STE] System Tray Extensions"

        signal.signal(signal.SIGINT, signal.SIG_DFL) # CTRL+C fix

        self.home_directory = str(Path.home())
        self.app_directory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.app_directory)

        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)

        # Adding item on the menu bar
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("icon.png"))
        self.tray.setVisible(True)

        # Add menu items from extensions
        self.menu = QMenu()

        # TODO: read settings and init extensions

        # TODO: remember last states

        self.menu.addSeparator()

        # About action
        # todo: check updates on start
        self.action_about = QAction("About")
        self.action_about.triggered.connect(lambda: webbrowser.open(self.repository_url) )
        self.menu.addAction(self.action_about)

        # Restart action
        self.action_restart = QAction("Restart App")
        self.action_restart.triggered.connect(self.restart_app)
        self.menu.addAction(self.action_restart)

        # Quit action
        self.action_exit = QAction("Exit App")
        self.action_exit.triggered.connect(self.exit_confirmation)
        self.menu.addAction(self.action_exit)

        self.tray.setContextMenu(self.menu)
        self.app.exec_()

    def exit_confirmation(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Are you sure to exit?")
        msgBox.setWindowTitle(self.app_title)
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            self.app.quit()

    def restart_app(self):
        os.execl(sys.executable, sys.executable, *sys.argv) # a quick hack
