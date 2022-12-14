import json
import tkinter as tk
from tkinter import BooleanVar, ttk
import spell
import keyboard
import psutil
from win32 import win32gui, win32process
import pyautogui
from playsound import playsound
import threading
import characterService
import time
import quickloot
from pynput import mouse
import ctypes

requireTibia = True
running = True

global spells
spells = {}

crosshair = None
updatingLootPositions = False
selectedPosition = None

config = {
    'offsetX': 0,
    'offsetY': 0,
    'offset_status_x': 0,
    'offset_status_y': 0,
    'player_center_position': {
        'updating': False,
        'x': 0,
        'y': 0,
        'thickness': 3
    },
    'world': 'venebra',
    'level': 318,
    'lastTimerName': '',
    'lastTimerDuration': 0,
    'lastTimerColor': '',
    'quicklootHotkey': 'alt+q',
    'lootPositions' : {
        "pos7": { 'position': 7, 'x': 871, 'y': 361 },
        "pos8": { 'position': 8, 'x': 943, 'y': 361 },
        "pos9": { 'position': 9, 'x': 1018, 'y': 361 },
        "pos4": { 'position': 4, 'x': 871, 'y': 436 },
        "pos5": { 'position': 5, 'x': 943, 'y': 436 },
        "pos6": { 'position': 6, 'x': 1018, 'y': 436 },
        "pos1": { 'position': 1, 'x': 871, 'y': 507 },
        "pos2": { 'position': 2, 'x': 943, 'y': 507 },
        "pos3": { 'position': 3, 'x': 1018, 'y': 507 }
    }
}

def intersects(x, y, x1, y1, x2, y2):
    if x >= x1 and x <= x2:
        if y >= y1 and y <= y2:
            return True
    return False

def saveConfigs():
    with open('config.json', 'w') as outfile:
        outfile.write(json.dumps(config, indent=4))

with open('config.json', 'r') as configFile:
    tempConfig = json.load(configFile)

    params = ['world', 'level', 'lastTimerName', 'lastTimerDuration', 'lastTimerColor', 'quicklootHotkey', 'lootPositions', 'offsetX',
        'offsetX', 'offsetY', 'offset_status_x', 'offset_status_y', 'player_center_position']

    for param in params:
        print('looking for the param: ' + param)
        if param in tempConfig:
            config[param] = tempConfig[param]
            print('loading ' + param + ' to config with value: ' + str(tempConfig[param]))
        else:
            config[param] = 0
            print('loading None for param: ' + param)

try:
    print(config['lootPositions']['pos1']['x'] == 0)
except:
    config['lootPositions'] = {
        "pos7": { 'position': 7, 'x': 871, 'y': 361 },
        "pos8": { 'position': 8, 'x': 943, 'y': 361 },
        "pos9": { 'position': 9, 'x': 1018, 'y': 361 },
        "pos4": { 'position': 4, 'x': 871, 'y': 436 },
        "pos5": { 'position': 5, 'x': 943, 'y': 436 },
        "pos6": { 'position': 6, 'x': 1018, 'y': 436 },
        "pos1": { 'position': 1, 'x': 871, 'y': 507 },
        "pos2": { 'position': 2, 'x': 943, 'y': 507 },
        "pos3": { 'position': 3, 'x': 1018, 'y': 507 }
    }
    saveConfigs()

preset = 'RP'

def current_mili_time():
    return round(time.time() * 1000)

def togglePreset():
    global preset
    global spells

    if preset == 'EK':
        preset = 'MS'
    elif preset == 'MS':
        preset = 'ED'
    elif preset == 'ED':
        preset = 'RP'
    elif preset == 'RP':
        preset = 'EK'

    spells = {}

    try:
        with open(preset + '.json', 'r') as presetFile:
            spells = json.load(presetFile)
    except:
        open(preset + '.json', 'a').close()

        
    try:
        with open('config.json', 'r') as configFile:
            config = json.load(configFile)
    except:
        open('config.json', 'a').close()

togglePreset()

def saveSpells():
    with open(preset + '.json', 'w') as outfile:
        outfile.write(json.dumps(spells, indent=4))

chatOn = False

processCheckInterval = 100000

mouseIsOver = False
hoverCounter = 0

screen = tk.Tk('spell cooldowns')
screen.attributes('-fullscreen', True)
screen.attributes('-transparentcolor', '#eee')
screen.attributes('-alpha', 0.7)
screen.attributes('-topmost', True)
#screen.overrideredirect(1)

offsetX = config['offsetX']
offsetY = config['offsetY']

move_status = False
offset_status_x = config['offset_status_x']
offset_status_y = config['offset_status_y']

user32 = ctypes.windll.user32

turning = False
if config['player_center_position'] == 0:
    player_center_position = {
        'updating': False,
        'x': user32.GetSystemMetrics(0) / 2,
        'y': user32.GetSystemMetrics(1) / 2,
        'thickness': 3
    }
else:
    player_center_position = config['player_center_position']


pressedX = 0
pressedY = 0

activeSpells = []

attackCd = spell.Spell('attackCd', 'yellow', 10000, 10000, height=5)
healingCd = spell.Spell('healingCd', 'green', 10000, 10000, height=5)
        

def tibiaIsRunning():
    print('looking for tibia...')
    for proc in psutil.process_iter():
        try:
            if 'client' in proc.name().lower():
                return True
        except:
            pass
    return False

def buttonPressed(event):
    global offsetX
    global pressedY
    global offsetY
    global pressedX
    global chatOn
    global attackCd
    global healingCd
    global move_status
    global selectedPosition
    global updatingLootPositions


    pressedX = event.x - offsetX
    pressedY = event.y - offsetY

    if (intersects(event.x, event.y, 1000 + 150 - 50 + offsetX, 350 + offsetY, 1000 + 150 + offsetX - 40, 350 + offsetY + 10)):
        player_center_position['updating'] = True
        return        

    if attackCd.intersects(event.x, event.y) or healingCd.intersects(event.x, event.y):
        move_status = True
        return

    if updatingLootPositions:
        for key in config['lootPositions']:
            position = config['lootPositions'][key]
            if event.x >= position['x'] - 10 and event.x <= position['x'] + 10 and event.y >= position['y'] - 10 and event.y <= position['y'] + 10:
                selectedPosition = position
                return


    if event.x >= 1000 + 150 - 40 + offsetX and event.x <= 1000 + 150 + offsetX - 30 and event.y >= 350 + offsetY and event.y <= 350 + offsetY + 10:
        if updatingLootPositions:
            selectedPosition = None
            saveConfigs()

        updatingLootPositions = not updatingLootPositions
        return

    if event.x >= 1000 + offsetX and event.x <= 1000 + offsetX + 10 and event.y >= 350 + offsetY and event.y <= 350 + offsetY + 10:
        chatOn = not chatOn
        return

    if event.x >= 1000 + 150 - 30 + offsetX and event.x <= 1000 + offsetX + 150 - 20 and event.y >= 350 + offsetY and event.y <= 350 + offsetY + 10:
            form = tk.Toplevel(screen)
            form.title('Find Players')
            form.geometry('200x150')
            screen.eval(f'tk::PlaceWindow {str(form)} center')

            tk.Label(form, text='world').grid(row = 0, column = 0)
            worldEntry = tk.Entry(form)
            worldEntry.insert(0, config['world'])
            worldEntry.grid(row = 0, column = 1)

            tk.Label(form, text='level').grid(row = 1, column = 0)
            levelEntry = tk.Entry(form)
            levelEntry.insert(0, config['level'])

            levelEntry.grid(row = 1, column = 1)

            def command(world, level):
                form.destroy()
                config['world'] = world
                config['level'] = level
                saveConfigs()
                
                characters = characterService.findPlayers(world, level)

                players = tk.Toplevel(screen)
                players.title('Players Dispon??veis')

                w = screen.winfo_reqwidth()
                h = screen.winfo_reqheight()
                ws = screen.winfo_screenwidth()
                hs = screen.winfo_screenheight()
                x = (ws/2) - (w/2)
                y = (hs/2) - (h/2)
                players.geometry('780x500')
                players.geometry('+%d+%d' % (x - 250, y - 250))

                container = tk.LabelFrame(players)
                container.pack(fill='both', expand=True, padx=10, pady=10)

                canvas = tk.Canvas(container)
                canvas.pack(side = tk.LEFT, fill='both', expand=True)

                yscrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview, width=20)
                yscrollbar.pack(side = tk.RIGHT, fill='y', expand=False)

                canvas.configure(yscrollcommand=yscrollbar.set)
                canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

                frame = tk.Frame(canvas)
                canvas.create_window(0, 0, window=frame, anchor='w')

                knights = []
                paladins = []
                sorcerers = []
                druids = []

                for character in characters:
                    if 'DRUID' in character['vocation'].upper():
                        druids.append(character)
                    elif 'SORCERER' in character['vocation'].upper():
                        sorcerers.append(character)
                    elif 'KNIGHT' in character['vocation'].upper():
                        knights.append(character)
                    elif 'PALADIN' in character['vocation'].upper():
                        paladins.append(character)

                tempMax = max(len(knights), len(paladins), len(sorcerers), len(druids))
                
                tempFrame = tk.Frame(frame)

                e = tk.Entry(tempFrame, width=30)
                e.insert(0, 'KNIGHTS: ' + str(len(knights)))
                e.config(state='readonly')
                e.pack(side=tk.LEFT)

                e = tk.Entry(tempFrame, width=30)
                e.insert(0, 'PALADINS: ' + str(len(paladins)))
                e.config(state='readonly')
                e.pack(side=tk.LEFT)

                e = tk.Entry(tempFrame, width=30)
                e.insert(0, 'SORCERERS: ' + str(len(sorcerers)))
                e.config(state='readonly')
                e.pack(side=tk.LEFT)

                e = tk.Entry(tempFrame, width=30)
                e.insert(0, 'DRUIDS: ' + str(len(druids)))
                e.config(state='readonly')
                e.pack(side=tk.LEFT)

                tempFrame.pack(expand=True, fill='x', anchor='w')

                for x in range(tempMax):
                    tempFrame = tk.Frame(frame)

                    if x < len(knights):
                        e = tk.Entry(tempFrame, width=30)
                        e.insert(0, knights[x]['name'] + ' - ' + str(knights[x]['level']))
                        e.config(state='readonly')
                        e.pack(side=tk.LEFT)
                    else:
                        e = tk.Entry(tempFrame, width=30)
                        e.insert(0, '')
                        e.config(state='readonly')
                        e.pack(side=tk.LEFT)


                    if x < len(paladins):
                        e = tk.Entry(tempFrame, width=30)
                        e.insert(0, paladins[x]['name'] + ' - ' + str(paladins[x]['level']))
                        e.config(state='readonly')
                        e.pack(side=tk.LEFT)
                    else:
                        e = tk.Entry(tempFrame, width=30)
                        e.insert(0, '')
                        e.config(state='readonly')
                        e.pack(side=tk.LEFT)

                    if x < len(sorcerers):
                        e = tk.Entry(tempFrame, width=30)
                        e.insert(0, sorcerers[x]['name'] + ' - ' + str(sorcerers[x]['level']))
                        e.config(state='readonly')
                        e.pack(side=tk.LEFT)
                    else:
                        e = tk.Entry(tempFrame, width=30)
                        e.insert(0, '')
                        e.config(state='readonly')
                        e.pack(side=tk.LEFT)

                    if x < len(druids):
                        e = tk.Entry(tempFrame, width=30)
                        e.insert(0, druids[x]['name'] + ' - ' + str(druids[x]['level']))
                        e.config(state='readonly')
                        e.pack(side=tk.LEFT)
                    else:
                        e = tk.Entry(tempFrame, width=30)
                        e.insert(0, '')
                        e.config(state='readonly')
                        e.pack(side=tk.LEFT)

                    tempFrame.pack(expand=True, fill='x', anchor='w')
                return

            tk.Button(form, text='busca', command=lambda: command(worldEntry.get(), levelEntry.get())).grid(row = 4, column = 0)
            tk.Button(form, text='exit', command=form.destroy).grid(row = 4, column = 2)

            return


    if event.x >= 1000 + 150 - 20 + offsetX and event.x <= 1000 + offsetX + 150 - 10 and event.y >= 350 + offsetY and event.y <= 350 + offsetY + 10:
        form = tk.Toplevel(screen)
        form.title('timer')
        screen.eval(f'tk::PlaceWindow {str(form)} center')

        tk.Label(form, text='texto').grid(row = 0, column = 0)
        textoEntry = tk.Entry(form)
        textoEntry.grid(row = 0, column = 1)
        textoEntry.insert(0, config['lastTimerName'])

        tk.Label(form, text='duracao').grid(row = 1, column = 0)
        durationEntry = tk.Entry(form)
        durationEntry.grid(row = 1, column = 1)
        durationEntry.insert(0, config['lastTimerDuration'])

        tk.Label(form, text='cor').grid(row = 2, column = 0)
        colorEntry = tk.Entry(form)
        colorEntry.grid(row = 2, column = 1)
        colorEntry.insert(0, config['lastTimerColor'])

        def addTimer():
            duration = 0
            if ':' in durationEntry.get():
                duration = ((int(durationEntry.get().split(':')[0])) * 60 + (int(durationEntry.get().split(':')[1]))) * 1000
            else:
                duration = int(durationEntry.get()) * 1000

            activeSpells.append(spell.Spell(textoEntry.get(), colorEntry.get(), duration, property='timer'))
            config['lastTimerName'] = textoEntry.get()
            config['lastTimerDuration'] = durationEntry.get()
            config['lastTimerColor'] = colorEntry.get()
            saveConfigs()
            form.destroy()

        addButton = tk.Button(form, text='add', command=addTimer).grid(row = 3, column = 0)
        exitButton = tk.Button(form, text='exit', command=form.destroy).grid(row = 3, column = 2)

        return



    if event.x >= 1000 + 150 - 10 + offsetX and event.x <= 1000 + offsetX + 150 and event.y >= 350 + offsetY and event.y <= 350 + offsetY + 10:
        form = tk.Toplevel(screen)
        form.title('Add skill')
        screen.eval(f'tk::PlaceWindow {str(form)} center')

        tempRow = 0

        tk.Label(form, text='text', anchor='w', justify=tk.LEFT).grid(row = 0, column = 0, sticky=tk.W)
        textoEntry = tk.Entry(form)
        textoEntry.grid(row = 0, column = 1)

        tk.Label(form, text='cooldown').grid(row = 1 , column = 0, sticky=tk.W)
        cooldownEntry = tk.Entry(form)
        cooldownEntry.grid(row = 1, column = 1)

        tk.Label(form, text='duration').grid(row = 2, column = 0, sticky=tk.W)
        durationEntry = tk.Entry(form)
        durationEntry.grid(row = 2, column = 1)

        tk.Label(form, text='color').grid(row = 4, column = 0, sticky=tk.W)
        colorEntry = tk.Entry(form)
        colorEntry.grid(row = 4, column = 1)

        tk.Label(form, text='type (substitute effect)').grid(row = 5, column = 0, sticky=tk.W)
        typeEntry = tk.Entry(form)
        typeEntry.grid(row = 5, column = 1)

        tk.Label(form, text='hotkey').grid(row = 6, column = 0, sticky=tk.W)
        hotkeyEnty = tk.Entry(form)
        hotkeyEnty.grid(row = 6, column = 1)

        def clearHotkey(e, hotkeyEnty):
            if e.keysym in ['Control_L', 'Shift_L', 'Alt_L', 'Control_R', 'Shift_R', 'Alt_R']:
                return 'break'

            hotkeyEnty.delete(0, 'end')
            if keyboard.is_pressed('ctrl'):
                hotkeyEnty.insert(0, 'ctrl+')
            if keyboard.is_pressed('shift'):
                hotkeyEnty.insert(0, 'shift+')
            if keyboard.is_pressed('alt'):
                hotkeyEnty.insert(0, 'alt+')

            if keyboard.is_pressed('ctrl'):
                if e.keysym in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']:
                    hotkeyEnty.insert('end', e.keysym.lower())
                else:
                    hotkeyEnty.insert('end', chr(e.keycode).lower())
            else:
                if keyboard.is_pressed('shift'):
                    if e.keysym in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']:
                        hotkeyEnty.insert('end', e.keysym.lower())
                    else:
                        hotkeyEnty.insert('end', chr(e.keycode).lower())
                else:
                    if e.keysym in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']:
                        hotkeyEnty.insert('end', e.keysym.lower())
                    else:
                        hotkeyEnty.insert('end', chr(e.keycode).lower())
            return 'break'

        hotkeyEnty.bind('<Key>', lambda e: clearHotkey(e, hotkeyEnty))

        tk.Label(form, text='Property').grid(row = 8, column = 0, sticky=tk.W)
        current_var = tk.StringVar()
        combobox = ttk.Combobox(form, textvariable=current_var)
        combobox['values'] = ['-', 'ATTACK', 'HEALING']
        combobox['state'] = 'readonly'
        current_var.set('-')
        combobox.set('-')
        combobox.grid(row = 8, column = 1)

        tk.Label(form, text='Crosshair').grid(row = 9, column = 0, sticky=tk.W)
        crosshairVar = tk.BooleanVar()
        crossHairCheck = tk.Checkbutton(form, variable=crosshairVar)
        crossHairCheck.grid(row = 9, column = 1, sticky='w')

        tk.Label(form, text='Play alert').grid(row = 10, column = 0, sticky=tk.W)
        alertVar = BooleanVar()
        alertCheck = tk.Checkbutton(form, variable=alertVar)
        alertCheck.grid(row = 10, column = 1, sticky='w')

        tk.Label(form, text='turn character?').grid(row = 11, column = 0, sticky=tk.W)
        turnCharacterVar = BooleanVar()
        turnCharacterCheck = tk.Checkbutton(form, variable=turnCharacterVar)
        turnCharacterCheck.grid(row = 11, column = 1, sticky='w')

        tk.Label(form, text='in-game hoykey').grid(row = 12, column = 0, sticky=tk.W)
        inGamehotkeyEnty = tk.Entry(form)
        inGamehotkeyEnty.grid(row = 12, column = 1)
        inGamehotkeyEnty.bind('<Key>', lambda e: clearHotkey(e, inGamehotkeyEnty))

        def addHk():
            spells[hotkeyEnty.get()] = { 'name': textoEntry.get(), 'color': colorEntry.get(), 'duration': int(durationEntry.get()) * 1000,
            'cooldown': int(cooldownEntry.get()) * 1000, 'type': typeEntry.get() }

            if current_var.get() != '' or current_var.get() != '-':
                if current_var.get() == 'ATTACK':
                    spells[hotkeyEnty.get()]['property'] = 'attack'
                elif current_var.get() == 'HEALING':
                    spells[hotkeyEnty.get()]['property'] = 'healing'

            spells[hotkeyEnty.get()]['crosshair'] = crosshairVar.get()
            
            if alertVar.get():
                spells[hotkeyEnty.get()]['property'] = 'timer'

            if turnCharacterVar.get():
                spells[hotkeyEnty.get()]['turnCharacter'] = True

            spells[hotkeyEnty.get()]['inGameHotkey'] = inGamehotkeyEnty.get()

            form.destroy()
            saveSpells()
            return

        buttonsCanvas = tk.Frame(form, bg='black')
        buttonsCanvas.grid(row = 13, column = 0, columnspan=2)

        tk.Button(buttonsCanvas, text='add', command=addHk, width=15).pack(side = tk.LEFT, fill = 'x', expand = True)
        tk.Button(buttonsCanvas, text='exit', command=form.destroy, width=15).pack(side = tk.RIGHT, fill = 'x', expand = True)

        return

def rightButtonPressed(event):
    if event.x >= 1000 + offsetX and event.x <= 1000 + offsetX + 150 and event.y >= 325 + offsetY and event.y <= 325 + offsetY + 20:
        togglePreset()

    for i, tempSpell in enumerate(activeSpells):
        if event.x >= 1000 + offsetX and event.x <= 1000 + offsetX + tempSpell.width and event.y >= 300 + offsetY - (i * 20) and event.y <= 300 + offsetY - (i * 20) + tempSpell.height:
            activeSpells.remove(tempSpell)
    

def buttonReleased(event):
    global move_status
    move_status = False
    global selectedPosition
    selectedPosition = None
    global move_target_area
    move_target_area = False
    global player_center_position

    if player_center_position['updating']:
        config['player_center_position'] = player_center_position
        player_center_position['updating'] = False
        saveConfigs()

screen.bind('<Button-1>', buttonPressed)
screen.bind('<ButtonRelease>', buttonReleased)
screen.bind('<Button-3>', rightButtonPressed)

def mouseDragged(event):
    global move_status

    global offsetX
    global offsetY

    global offset_status_x
    global offset_status_y

    if (player_center_position['updating']):
        player_center_position['x'] = event.x
        player_center_position['y'] = event.y
        return

    if selectedPosition != None:
        pos_dx = selectedPosition['x'] - event.x
        pos_dy = selectedPosition['y'] - event.y

        if selectedPosition['position'] == 5:
            selectedPosition['x'] = event.x
            selectedPosition['y'] = event.y
            for key in config['lootPositions']:
                position = config['lootPositions'][key]
                if position != selectedPosition:
                    position['x'] -= pos_dx
                    position['y'] -= pos_dy
            return

        if selectedPosition['position'] == 1:
            selectedPosition['x'] = event.x
            selectedPosition['y'] = event.y
            config['lootPositions']['pos2']['y'] = selectedPosition['y']
            config['lootPositions']['pos3']['y'] = selectedPosition['y']
            config['lootPositions']['pos4']['x'] = selectedPosition['x']
            config['lootPositions']['pos7']['x'] = selectedPosition['x']
        if selectedPosition['position'] == 2:
            selectedPosition['y'] = event.y
            config['lootPositions']['pos1']['y'] = selectedPosition['y']
            config['lootPositions']['pos3']['y'] = selectedPosition['y']
        if selectedPosition['position'] == 3:
            selectedPosition['x'] = event.x
            selectedPosition['y'] = event.y
            config['lootPositions']['pos1']['y'] = selectedPosition['y']
            config['lootPositions']['pos2']['y'] = selectedPosition['y']
            config['lootPositions']['pos6']['x'] = selectedPosition['x']
            config['lootPositions']['pos9']['x'] = selectedPosition['x']
        if selectedPosition['position'] == 4:
            selectedPosition['x'] = event.x
            config['lootPositions']['pos1']['x'] = selectedPosition['x']
            config['lootPositions']['pos7']['x'] = selectedPosition['x']
        if selectedPosition['position'] == 6:
            selectedPosition['x'] = event.x
            config['lootPositions']['pos3']['x'] = selectedPosition['x']
            config['lootPositions']['pos9']['x'] = selectedPosition['x']
        if selectedPosition['position'] == 7:
            selectedPosition['x'] = event.x
            selectedPosition['y'] = event.y
            config['lootPositions']['pos8']['y'] = selectedPosition['y']
            config['lootPositions']['pos9']['y'] = selectedPosition['y']
            config['lootPositions']['pos4']['x'] = selectedPosition['x']
            config['lootPositions']['pos1']['x'] = selectedPosition['x']
        if selectedPosition['position'] == 8:
            selectedPosition['y'] = event.y
            config['lootPositions']['pos7']['y'] = selectedPosition['y']
            config['lootPositions']['pos9']['y'] = selectedPosition['y']
        if selectedPosition['position'] == 9:
            selectedPosition['x'] = event.x
            selectedPosition['y'] = event.y
            config['lootPositions']['pos7']['y'] = selectedPosition['y']
            config['lootPositions']['pos8']['y'] = selectedPosition['y']
            config['lootPositions']['pos6']['x'] = selectedPosition['x']
            config['lootPositions']['pos3']['x'] = selectedPosition['x']

        config['lootPositions']['pos5']['x'] = ( config['lootPositions']['pos4']['x'] + config['lootPositions']['pos6']['x']) / 2
        config['lootPositions']['pos5']['y'] = ( config['lootPositions']['pos2']['y'] + config['lootPositions']['pos8']['y']) / 2

        if config['lootPositions']['pos2'] != selectedPosition:
            config['lootPositions']['pos2']['x'] = ( config['lootPositions']['pos4']['x'] + config['lootPositions']['pos6']['x']) / 2

        if config['lootPositions']['pos8'] != selectedPosition:
            config['lootPositions']['pos8']['x'] = ( config['lootPositions']['pos4']['x'] + config['lootPositions']['pos6']['x']) / 2

        if config['lootPositions']['pos4'] != selectedPosition:
            config['lootPositions']['pos4']['y'] = ( config['lootPositions']['pos2']['y'] + config['lootPositions']['pos8']['y']) / 2

        if config['lootPositions']['pos6'] != selectedPosition:
            config['lootPositions']['pos6']['y'] = ( config['lootPositions']['pos2']['y'] + config['lootPositions']['pos8']['y']) / 2
        
        


        return

    if move_status:
        attackCd.width = 50
        healingCd.width = 50
        attackCd.height = 4
        healingCd.height = 4
        offset_status_x = event.x - pressedX
        offset_status_y = event.y - pressedY
        return
    else:
        attackCd.width = 150
        healingCd.width = 150
        attackCd.height = 5
        healingCd.height = 5

    offsetX = event.x - pressedX
    offsetY = event.y - pressedY

    offset_status_x = event.x - pressedX
    offset_status_y = event.y - pressedY

    config['offsetX'] = offsetX
    config['offsetY'] = offsetY
    config['offset_status_x'] = offset_status_x
    config['offset_status_y'] = offset_status_y
    saveConfigs()

screen.bind('<B1-Motion>', mouseDragged)

def close(event):
    global running
    running = False
    screen.destroy()

screen.bind('<Escape>', close)

canvas = tk.Canvas(screen, highlightthickness = 0, bg='#eee')
canvas.pack(fill=tk.BOTH, expand=True)
canvas.bind('')

def getProcessName():
    try:
        pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
        return psutil.Process(pid[-1]).name()
    except:
        pass


def addSpell(tempSpell): 
    if not 'tempSpell' in locals():
        return

    try:
        for s in activeSpells:
            if s.type != None and s.type != '' and s.type == tempSpell.type:
                activeSpells.remove(s)

        activeSpells.remove(tempSpell)
    except:
        pass

    activeSpells.append(tempSpell)

    if tempSpell.property == 'attack':
        global attackCd
        attackCd = spell.Spell('attackCd', 'yellow', tempSpell.cooldown, 2000, height=attackCd.height, width = attackCd.width)
    if tempSpell.property == 'healing':
        global healingCd
        healingCd = spell.Spell('healingCd', 'green', tempSpell.cooldown, 1000, height=healingCd.height, width = healingCd.width)


def key_press(key):
    global config
    global turning

    if turning:
        return

    if requireTibia and getProcessName() != 'client.exe':
        return

    if key.name == 'enter':
        global chatOn
        chatOn = not chatOn

    if chatOn:
        return

    keyName = ''
    if keyboard.is_pressed('ctrl'):
        keyName += 'ctrl+'
    if keyboard.is_pressed('alt'):
        keyName += 'alt+'
    if keyboard.is_pressed('shift'):
        keyName += 'shift+'
    keyName += key.name.lower()

    if keyName.lower() == config['quicklootHotkey']:
        threading.Thread(target = lambda: quickloot.quickLoot(config['lootPositions'])).start()
        return

    selectedSpell = None
    if keyName in spells:
        selectedSpell = spells[keyName]
    else:
        return

    if selectedSpell.get('turnCharacter'):
        turning = True

        x = pyautogui.position().x
        y = pyautogui.position().y

        dx = x - player_center_position['x']
        dy = y - player_center_position['y']

        downTime = 0.03
        keyboard.press('ctrl')
        time.sleep(downTime)
        directionKey = ''
        if (abs(dx) > abs(dy)): #HORIZONTAL
            if (dx > 0):
                directionKey = 'right'
            if (dx < 0):
                directionKey = 'left'
        else: #VERTICAL
            if (dy > 0):
                directionKey = 'down'
            if (dy < 0):
                directionKey = 'up'
        keyboard.press(directionKey)
        time.sleep(downTime)
        keyboard.release(directionKey)
        time.sleep(downTime)
        keyboard.release('ctrl')

        hotkey = selectedSpell['inGameHotkey']
        modifiers = []
        if 'ctrl' in selectedSpell.get('inGameHotkey'):
            keyboard.press('ctrl')
            time.sleep(0.01)
            modifiers.append('ctrl')
            hotkey = selectedSpell.get('inGameHotkey').replace('ctrl+', '')
        if 'alt' in selectedSpell.get('inGameHotkey'):
            keyboard.press('alt')
            time.sleep(0.01)
            modifiers.append('alt')
            hotkey = selectedSpell.get('inGameHotkey').replace('alt+', '')
        if 'shift' in selectedSpell.get('inGameHotkey'):
            keyboard.press('shift')
            time.sleep(0.01)
            modifiers.append('shift')
            hotkey = selectedSpell.get('inGameHotkey').replace('shift+', '')

        keyboard.press(hotkey)
        time.sleep(0.01)
        keyboard.release(hotkey)

        for key in modifiers:
            keyboard.release(key)
        
    tempSpell = spell.Spell(selectedSpell.get('name'), selectedSpell.get('color'), selectedSpell.get('duration'), selectedSpell.get('cooldown'),
        selectedSpell.get('type'), selectedSpell.get('property'), selectedSpell.get('turnCharacter'), selectedSpell.get('inGameHotkey'))

    try:
        tempSpell.crosshair = selectedSpell.get('crosshair')
    except:
        tempSpell.crosshair = False

    if tempSpell.crosshair:
        global crosshair
        crosshair = tempSpell
        return

    def changeTurning():
        global turning
        time.sleep(0.01)
        turning = False

    threading.Thread(target=changeTurning).start()

    addSpell(tempSpell)

keyboard.on_press(key_press)

def on_click(x, y, button, pressed):
    global crosshair

    if crosshair != None and button == mouse.Button.left:
        crosshair = spell.Spell(crosshair.name, crosshair.color, crosshair.duration, crosshair.cooldown, crosshair.type, crosshair.property, crosshair.width, crosshair.height, False)
        addSpell(crosshair)
        pass

    crosshair = None

listener = mouse.Listener(on_click=on_click)
listener.start()

def lookForTibia():
    global requireTibia
    if tibiaIsRunning():
        requireTibia = True
    else:
        requireTibia = False

lookForTibia()

while running:
    mouseX = pyautogui.position().x
    mouseY = pyautogui.position().y

    if len(activeSpells) == 0 and current_mili_time() % processCheckInterval == 0:
        threading.Thread(target=lookForTibia).start()

    if getProcessName() != 'client.exe' and requireTibia and ((mouseX >= 1000 + offsetX and mouseX <= 1150 + offsetX and mouseY <= 360 + offsetY and mouseY >= 320 - (len(activeSpells) * 20) + offsetY) or attackCd.intersects(mouseX, mouseY) or healingCd.intersects(mouseX, mouseY)):
        mouseIsOver = True
        hoverCounter += 1
    else:
        mouseIsOver = False
        hoverCounter = 0

    canvas.delete('all')

    if (player_center_position['updating']):
        canvas.create_rectangle(
            player_center_position['x'] - player_center_position['thickness'],
            player_center_position['y'] - 20,
            player_center_position['x'] + player_center_position['thickness'],
            player_center_position['y'] + 20,
            fill='white'
        )

        canvas.create_rectangle(
            player_center_position['x'] - 20,
            player_center_position['y'] - player_center_position['thickness'],
            player_center_position['x'] + 20,
            player_center_position['y'] + player_center_position['thickness'],
            fill='white'
        )



    if requireTibia and getProcessName() != 'client.exe' and getProcessName() not in ['python.exe', 'cooldowns.exe']:
        canvas.update()
        continue

    if not mouseIsOver or keyboard.is_pressed('alt') or not requireTibia:
        lastHeight = 0
        for i, tempSpell in enumerate(activeSpells):
            #tempSpell.draw(canvas, 1000 + offsetX, 300 - ((i) * lastHeight) + offsetY)
            tempSpell.x = 1000 + offsetX
            tempSpell.y = 300 - ((i) * lastHeight) + offsetY
            tempSpell.draw(canvas)
            lastHeight = tempSpell.height

            if tempSpell.timeLeft() <= 0:
                if tempSpell.property == 'timer':
                    threading.Thread(target=lambda: playsound('./alert.wav')).start()

                activeSpells.remove(tempSpell)

        canvas.create_rectangle(1000 + offsetX, 330 + offsetY, 1000 + offsetX + 150, 330 + offsetY + 20, fill='white')
        canvas.create_text(1002 + offsetX, 340 + offsetY, fill='black', text='Preset:', anchor='w')
        canvas.create_text(1140 + offsetX, 340 + offsetY, fill='black', text=preset, anchor='e')

        if chatOn:
            canvas.create_rectangle(1000 + offsetX, 350 + offsetY, 1000 + offsetX + 10, 350 + offsetY + 10, fill='red')
        
        canvas.create_rectangle(1000 + 150 - 10 + offsetX, 350 + offsetY, 1000 + 150 + offsetX, 350 + offsetY + 10, fill='blue')
        canvas.create_rectangle(1000 + 150 - 20 + offsetX, 350 + offsetY, 1000 + 150 + offsetX - 10, 350 + offsetY + 10, fill='yellow')
        canvas.create_rectangle(1000 + 150 - 30 + offsetX, 350 + offsetY, 1000 + 150 + offsetX - 20, 350 + offsetY + 10, fill='green')
        canvas.create_rectangle(1000 + 150 - 40 + offsetX, 350 + offsetY, 1000 + 150 + offsetX - 30, 350 + offsetY + 10, fill='orange')
        canvas.create_rectangle(1000 + 150 - 50 + offsetX, 350 + offsetY, 1000 + 150 + offsetX - 40, 350 + offsetY + 10, fill='white')

        if attackCd:
            tempAttackCd = spell.Spell(name='attackCd', color='yellow', duration=attackCd.duration, cooldown=attackCd.cooldown, width=150, height=5)
            tempAttackCd.start = attackCd.start
            tempAttackCd.x = 1000 + offsetX
            tempAttackCd.y = 320 + offsetY
            tempAttackCd.color = attackCd.color
            tempAttackCd.draw(canvas)

            attackCd.x = 1000 + offset_status_x
            attackCd.y = 320 + offset_status_y
            canvas.create_rectangle(attackCd.x, attackCd.y, attackCd.x + attackCd.width, attackCd.y + attackCd.height, fill='gray')
            attackCd.draw(canvas)
            if attackCd.timeLeft() <= 0:
                if round(attackCd.timeLeft(), 1) * 10 % 2 == 0:
                    attackCd.color = 'yellow'
                else:
                    attackCd.color = 'red'
        
        if healingCd:
            tempHealing = spell.Spell(name='healingCd', color='green', duration=healingCd.duration, cooldown=healingCd.cooldown, width=150, height=5)
            tempHealing.start = healingCd.start
            tempHealing.x = 1000 + offsetX
            tempHealing.y = 325 + offsetY
            tempHealing.color = healingCd.color
            tempHealing.draw(canvas)

            healingCd.x = 1000 + offset_status_x
            healingCd.y = 325 + offset_status_y
            canvas.create_rectangle(healingCd.x, healingCd.y, healingCd.x + healingCd.width, healingCd.y + healingCd.height, fill='gray')
            healingCd.draw(canvas)
            if healingCd.timeLeft() <= 0:
                healingCd.color = 'white'


    if updatingLootPositions:
        for key in config['lootPositions']:
            position = config['lootPositions'][key]
            canvas.create_rectangle(position['x'] - 10, position['y'] - 10, position['x'] + 10, position['y'] + 10, fill='green')
            canvas.create_text(position['x'], position['y'], text=position['position'], anchor='c', fill='white')
    canvas.update()