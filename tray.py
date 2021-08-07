from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from ite8291r3_ctl import ite8291r3


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

turnoff = QAction("Turn Off")
menu.addAction(turnoff)
exec("turnoff.triggered.connect(lambda: ite.turn_off() )")

testpattern = QAction("Test Pattern")
menu.addAction(testpattern)
exec("testpattern.triggered.connect(lambda: ite.test_pattern() )")

freeze = QAction("Freeze")
menu.addAction(freeze)
exec("freeze.triggered.connect(lambda: ite.freeze() )")


menu.addSeparator()

incbrightness = QAction("Increase Brightness")
menu.addAction(incbrightness)
exec("incbrightness.triggered.connect(lambda: ite.set_brightness(ite.get_brightness()+10) )")

decbrightness = QAction("Decrease Brightness")
menu.addAction(decbrightness)
exec("decbrightness.triggered.connect(lambda: ite.set_brightness(ite.get_brightness()-10) )")

menu.addSeparator()


colors = {"red":    (255,   0,   0),
          "orange": (255,  28,   0),
          "yellow": (255, 119,   0),
          "green":  (  0, 255,   0),
          "blue":   (  0,   0, 255),
          "teal":   (  0, 255, 255),
          "purple": (255,   0, 255),
          }

qactions_colors = {}
for k,v in colors.items():
    action = QAction(k.capitalize())
    qactions_colors[k] = action
    menu.addAction(action)
    exec("action.triggered.connect(lambda: ite.set_color("+str(v)+"))")

menu.addSeparator()

# Creating the options dynamically
qactions_effects = {}
for k,v in ite8291r3.effects.items():
    action = QAction(k.capitalize())
    qactions_effects[k] = action
    menu.addAction(action)
    exec("action.triggered.connect(lambda: ite.set_effect( ite8291r3.effects[\""+k+"\"]()) )")


menu.addSeparator()

# To quit the app
quit = QAction("Quit")
quit.triggered.connect(app.quit)
menu.addAction(quit)
  
# Adding options to the System Tray
tray.setContextMenu(menu)
  
app.exec_()
