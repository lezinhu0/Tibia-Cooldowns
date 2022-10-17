from audioop import cross
import json
import tkinter as tk
from tkinter import ttk
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

requireTibia = False
running = True

global spells
spells = {}

crosshair = None

config = {
    'world': 'venebra',
    'level': 318,
    'lastTimerName': '',
    'lastTimerDuration': 0,
    'lastTimerColor': '',
    'quicklootHotkey': 'alt+q'
}

try:
    with open('config.json', 'r') as configFile:
        tempConfig = json.load(configFile)

        if tempConfig['world']: config['world'] = tempConfig['world']
        if tempConfig['level']: config['level'] = tempConfig['level']
        if tempConfig['lastTimerName']: config['lastTimerName'] = tempConfig['lastTimerName']
        if tempConfig['lastTimerDuration']: config['lastTimerDuration'] = tempConfig['lastTimerDuration']
        if tempConfig['lastTimerColor']: config['lastTimerColor'] = tempConfig['lastTimerColor']
        if tempConfig['quicklootHotkey']: config['quicklootHotkey'] = tempConfig['quicklootHotkey']
except:
    pass

def saveConfigs():
    with open('config.json', 'w') as outfile:
        outfile.write(json.dumps(config, indent=4))

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

processCheckInterval = 10000

mouseIsOver = False
hoverCounter = 0

screen = tk.Tk('spell cooldowns')
screen.attributes('-fullscreen', True)
screen.attributes('-transparentcolor', '#eee')
screen.attributes('-alpha', 0.7)
screen.attributes('-topmost', True)
screen.overrideredirect(1)

offsetX = 0
offsetY = 0

pressedX = 0
pressedY = 0

activeSpells = []

attackCd = None
healingCd = None

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
                players.title('Players Disponíveis')

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

            tk.Button(form, text='add', command=lambda: command(worldEntry.get(), levelEntry.get())).grid(row = 4, column = 0)
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

        tk.Label(form, text='type (replace effect)').grid(row = 5, column = 0, sticky=tk.W)
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

        tk.Label(form, text='Crosshair?').grid(row = 9, column = 0, sticky=tk.W)
        crosshairVar = tk.BooleanVar()
        crossHairCheck = tk.Checkbutton(form, variable=crosshairVar)
        crossHairCheck.grid(row = 9, column = 1, sticky='w')

        def addHk():
            spells[hotkeyEnty.get()] = { 'name': textoEntry.get(), 'color': colorEntry.get(), 'duration': int(durationEntry.get()) * 1000,
            'cooldown': int(cooldownEntry.get()) * 1000, 'type': typeEntry.get() }

            if current_var.get() != '' or current_var.get() != '-':
                if current_var.get() == 'ATTACK':
                    spells[hotkeyEnty.get()]['property'] = 'attack'
                elif current_var.get() == 'HEALING':
                    spells[hotkeyEnty.get()]['property'] = 'healing'

            spells[hotkeyEnty.get()]['crosshair'] = crosshairVar.get()

            form.destroy()
            saveSpells()
            return

        buttonsCanvas = tk.Frame(form, bg='black')
        buttonsCanvas.grid(row = 10, column = 0, columnspan=2)

        tk.Button(buttonsCanvas, text='add', command=addHk, width=15).pack(side = tk.LEFT, fill = 'x', expand = True)
        tk.Button(buttonsCanvas, text='exit', command=form.destroy, width=15).pack(side = tk.RIGHT, fill = 'x', expand = True)

        return

    pressedX = event.x - offsetX
    pressedY = event.y - offsetY

def rightButtonPressed(event):
    if event.x >= 1000 + offsetX and event.x <= 1000 + offsetX + 150 and event.y >= 325 + offsetY and event.y <= 325 + offsetY + 20:
        togglePreset()

    for i, tempSpell in enumerate(activeSpells):
        if event.x >= 1000 + offsetX and event.x <= 1000 + offsetX + tempSpell.width and event.y >= 300 + offsetY - (i * 20) and event.y <= 300 + offsetY - (i * 20) + tempSpell.height:
            activeSpells.remove(tempSpell)
    

screen.bind('<Button-1>', buttonPressed)
screen.bind('<Button-3>', rightButtonPressed)

def mouseDragged(event):
    global offsetX
    offsetX = event.x - pressedX
    global offsetY
    offsetY = event.y - pressedY

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
        attackCd = spell.Spell('attackCd', 'yellow', tempSpell.cooldown, 2000, height=5)
    if tempSpell.property == 'healing':
        global healingCd
        healingCd = spell.Spell('healingCd', 'green', tempSpell.cooldown, 1000, height=5)


def key_press(key):
    global config
    
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
        threading.Thread(target = quickloot.quickLoot).start()
        return

    selectedSpell = None
    if keyName in spells:
        selectedSpell = spells[keyName]
    else:
        return

    tempSpell = spell.Spell(selectedSpell.get('name'), selectedSpell.get('color'), selectedSpell.get('duration'), selectedSpell.get('cooldown'),
        selectedSpell.get('type'), selectedSpell.get('property'))

    try:
        tempSpell.crosshair = selectedSpell.get('crosshair')
    except:
        tempSpell.crosshair = False

    if tempSpell.crosshair:
        global crosshair
        crosshair = tempSpell
        return


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

while running:
    mouseX = pyautogui.position().x
    mouseY = pyautogui.position().y

    if len(activeSpells) == 0 and current_mili_time() % processCheckInterval == 0:
        threading.Thread(target=lookForTibia).start()

    if requireTibia and mouseX >= 1000 + offsetX and mouseX <= 1150 + offsetX and mouseY <= 360 + offsetY and mouseY >= 320 - (len(activeSpells) * 20) + offsetY:
        mouseIsOver = True
        hoverCounter += 1
    else:
        mouseIsOver = False
        hoverCounter = 0

    canvas.delete('all')

    if requireTibia and getProcessName() != 'client.exe' and getProcessName() not in ['python.exe', 'cooldowns.exe']:
        canvas.update()
        continue


    if not mouseIsOver or keyboard.is_pressed('alt') or not requireTibia:
        lastHeight = 0
        for i, tempSpell in enumerate(activeSpells):
            tempSpell.draw(canvas, 1000 + offsetX, 300 - ((i) * lastHeight) + offsetY)
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

        if attackCd:
            attackCd.draw(canvas, 1000 + offsetX, 320 + offsetY)
            if attackCd.timeLeft() <= 0:
                if round(attackCd.timeLeft(), 1) * 10 % 2 == 0:
                    attackCd.color = 'yellow'
                else:
                    attackCd.color = 'red'
        
        if healingCd:
            healingCd.draw(canvas, 1000 + offsetX, 325 + offsetY)
            if healingCd.timeLeft() <= 0:
                healingCd.color = 'white'

    canvas.update()