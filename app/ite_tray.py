from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from ite8291r3_ctl import ite8291r3
import webbrowser


import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


ite = ite8291r3.get()


app = QApplication([])
app.setQuitOnLastWindowClosed(False)
  
# Adding an icon
icon = QIcon("icon.png")
  
# Adding item on the menu bar
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

menu = QMenu()


effect_menu = QMenu("Effects")

# Creating the options dynamically
qactions_effects = {}
for k,v in ite8291r3.effects.items():
    action = QAction(k.capitalize())
    qactions_effects[k] = action
    effect_menu.addAction(action)
    exec("action.triggered.connect(lambda: ite.set_effect( ite8291r3.effects[\""+k+"\"]()) )")

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
    color_menu.addAction(action)
    exec("action.triggered.connect(lambda: ite.set_color("+str(v)+"))")

menu.addMenu(color_menu)



menu.addSeparator() #================================================================


incbrightness = QAction("Increase Brightness")
menu.addAction(incbrightness)
exec("incbrightness.triggered.connect(lambda: ite.set_brightness(ite.get_brightness()+10) )")

decbrightness = QAction("Decrease Brightness")
menu.addAction(decbrightness)
exec("decbrightness.triggered.connect(lambda: ite.set_brightness(ite.get_brightness()-10) )")

menu.addSeparator() #================================================================


turnoff = QAction("Turn Off Keyboard Backlight")
menu.addAction(turnoff)
exec("turnoff.triggered.connect(lambda: ite.turn_off() )")

freeze = QAction("Freeze Animation")
menu.addAction(freeze)
exec("freeze.triggered.connect(lambda: ite.freeze() )")

testpattern = QAction("Test Pattern")
menu.addAction(testpattern)
exec("testpattern.triggered.connect(lambda: ite.test_pattern() )")

menu.addSeparator() #================================================================


about = QAction("About")
project_webpage_url = "https://github.com/salihmarangoz/ite8291r3-gui"
exec("about.triggered.connect(lambda: webbrowser.open(project_webpage_url) )")
menu.addAction(about)


def exit_confirmation():
   msgBox = QMessageBox()
   msgBox.setIcon(QMessageBox.Question)
   msgBox.setText("Are you sure to exit?")
   msgBox.setWindowTitle("Keyboard Backlight GUI")
   msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

   returnValue = msgBox.exec()
   if returnValue == QMessageBox.Yes:
      app.quit()

# To quit the app
quit = QAction("Quit")
quit.triggered.connect(exit_confirmation)
menu.addAction(quit)


# Adding options to the System Tray
tray.setContextMenu(menu)
  
app.exec_()
