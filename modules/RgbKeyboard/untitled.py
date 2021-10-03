


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


ite = ite8291r3.get()