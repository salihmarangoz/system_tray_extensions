from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from ite8291r3_ctl import ite8291r3
import webbrowser
import os
from pathlib import Path
import numpy as np
from PIL import Image
import glob
import sys

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


#################### FUNCTIONS #####################################

def create_empty_image(fill_value=(80,80,80)):
    img = np.ones((6*20+7*5, 18*20+19*5, 3), dtype=np.uint8)*255

    for i in range(7):
        img[i*25:i*25+5, :] = fill_value

    for j in range(19):
        img[:, j*25:j*25+5] = fill_value

    return img

def image_to_color_map(img):
    color_map = {}
    for i in range(6):
        for j in range(18):
            color_map[(5-i,j)] = tuple(img[i*25+12, j*25+12])
    return color_map

def save_img(filename, img):
    img_ = Image.fromarray(img)
    img_.save(filename, "PNG")

def open_img(filename, gamma_correction = (2.0, 3.0, 7.0)):
    img_ = Image.open(filename)
    img = np.array(img_, dtype=np.float32)[:,:,:3] / 255.0
    img = img**gamma_correction
    img = np.array(img*255, dtype=np.uint8)
    return img

def exit_confirmation():
  msgBox = QMessageBox()
  msgBox.setIcon(QMessageBox.Question)
  msgBox.setText("Are you sure to exit?")
  msgBox.setWindowTitle("Keyboard Backlight GUI")
  msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

  returnValue = msgBox.exec()
  if returnValue == QMessageBox.Yes:
     app.quit()


previous_brightness = 50
def toggle_onoff():
    global previous_brightness
    current_brightness = ite.get_brightness()
    if current_brightness > 0:
        previous_brightness = current_brightness
        ite.set_brightness(0)
    else:
        ite.set_brightness(previous_brightness)


create_menu_memory = [] # this is needed because garbage collector removes actions after the function returns
def create_menu():
    create_menu_memory.clear()

    menu = QMenu()

    toggle = QAction("Toggle On/Off")
    create_menu_memory.append(toggle)
    menu.addAction(toggle)
    exec("toggle.triggered.connect(lambda: toggle_onoff() )")

    incbrightness = QAction("Increase Brightness")
    create_menu_memory.append(incbrightness)
    menu.addAction(incbrightness)
    exec("incbrightness.triggered.connect(lambda: ite.set_brightness(min(ite.get_brightness()+10,50)) )")

    decbrightness = QAction("Decrease Brightness")
    create_menu_memory.append(decbrightness)
    menu.addAction(decbrightness)
    exec("decbrightness.triggered.connect(lambda: ite.set_brightness(max(ite.get_brightness()-10,10)) )")

    menu.addSeparator() #================================================================

    effect_menu = QMenu("Effects")

    # Creating the options dynamically
    qactions_effects = {}
    for k,v in ite8291r3.effects.items():
        action = QAction(k.capitalize())
        qactions_effects[k] = action
        create_menu_memory.append(action)
        effect_menu.addAction(action)
        exec("action.triggered.connect(lambda: ite.set_effect( ite8291r3.effects[\""+k+"\"]()) )")

    create_menu_memory.append(effect_menu)
    menu.addMenu(effect_menu)

    colors = {"white":  (255, 255, 255),
             "red":    (255,   0,   0),
             "orange": (255,  28,   0),
             "yellow": (255, 119,   0),
             "green":  (  0, 255,   0),
             "blue":   (  0,   0, 255),
             "teal":   (  0, 255, 255),
             "purple": (255,   0, 255),
             }

    color_menu = QMenu("Mono Color")

    qactions_colors = {}
    for k,v in colors.items():
        action = QAction(k.capitalize())
        qactions_colors[k] = action
        create_menu_memory.append(action)
        color_menu.addAction(action)
        exec("action.triggered.connect(lambda: ite.set_color("+str(v)+"))")

    create_menu_memory.append(color_menu)
    menu.addMenu(color_menu)

    custom_layout_menu = QMenu("Custom Layouts")

    custom_layouts = {}
    custom_layout_path = os.path.join(homedir, ".ite_tray_layouts")
    default_layout_file = os.path.join(custom_layout_path, "default.png")
    os.makedirs(custom_layout_path, exist_ok=True)
    if not os.path.isfile(default_layout_file):
        img = create_empty_image()
        save_img(default_layout_file, img)

    layout_files = glob.glob(custom_layout_path + '/*.png', recursive=True)
    qactions_custom = {}
    for f in layout_files:
        if "/default.png" in f:
            continue
        img = open_img(f)
        color_map = image_to_color_map(img)

        action = QAction(os.path.splitext(os.path.basename(f))[0].capitalize())
        #action = QAction(f.capitalize())
        qactions_custom[k] = action
        create_menu_memory.append(action)
        custom_layout_menu.addAction(action)

        create_menu_memory.append(color_map) # little tricks goes here
        exec("action.triggered.connect(lambda: ite.set_key_colors(create_menu_memory["+str(len(create_menu_memory)-1)+"]))")


    action = QAction("[Refresh list]")
    create_menu_memory.append(action)
    custom_layout_menu.addAction(action)
    exec("action.triggered.connect(lambda: os.execl(sys.executable, sys.executable, *sys.argv))") # quick hack

    create_menu_memory.append(custom_layout_menu)
    menu.addMenu(custom_layout_menu)

    menu.addSeparator() #================================================================

    freeze = QAction("Freeze Animation")
    create_menu_memory.append(freeze)
    menu.addAction(freeze)
    exec("freeze.triggered.connect(lambda: ite.freeze() )")

    testpattern = QAction("Test Pattern")
    create_menu_memory.append(testpattern)
    menu.addAction(testpattern)
    exec("testpattern.triggered.connect(lambda: ite.test_pattern() )")

    menu.addSeparator() #================================================================


    about = QAction("About")
    project_webpage_url = "https://github.com/salihmarangoz/ite8291r3-gui"
    exec("about.triggered.connect(lambda: webbrowser.open(project_webpage_url) )")
    create_menu_memory.append(about)
    menu.addAction(about)

    # To quit the app
    quit = QAction("Quit")
    quit.triggered.connect(exit_confirmation)
    create_menu_memory.append(quit)
    menu.addAction(quit)

    return menu

#################################################################


homedir = str(Path.home())
os.chdir(os.path.dirname(os.path.abspath(__file__)))

ite = ite8291r3.get()

app = QApplication([])
app.setQuitOnLastWindowClosed(False)
  
# Adding an icon
icon = QIcon("icon.png")
  
# Adding item on the menu bar
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

menu = create_menu()
tray.setContextMenu(menu) # Adding options to the System Tray
app.exec_()
