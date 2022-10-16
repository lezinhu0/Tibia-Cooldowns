import time
import tkinter as tk
from tkinter import ttk
from turtle import color
import spell
import keyboard
import win32gui, win32process, psutil
import pyautogui

spells = {}

preset = 'ek'
#preset = 'ms'

requireTibia = False

chatOn = False

processCheckInterval = 1000000

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

spells = []

attackCd = None

def tibiaIsRunning():
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

    if event.x >= 1000 + 150 - 10 + offsetX and event.x <= 1000 + offsetX + 150 and event.y >= 345 + offsetY and event.y <= 345 + offsetY + 10:
        form = tk.Toplevel(screen)

        tk.Label(form, text='text').grid(row = 0, column = 0)
        textInput = tk.Entry(form).grid(row = 0, column = 1)

        tk.Label(form, text='cooldown').grid(row = 1, column = 0)
        textInput = tk.Entry(form).grid(row = 1, column = 1)

        tk.Label(form, text='active time').grid(row = 2, column = 0)
        textInput = tk.Entry(form).grid(row = 2, column = 1)

        tk.Label(form, text='hotkey').grid(row = 3, column = 0)
        textInput = tk.Entry(form).grid(row = 3, column = 1)


        button = tk.Button(form, text='exit', command=form.destroy)
        button.grid(row = 4, column = 0)

        return

    pressedX = event.x - offsetX
    pressedY = event.y - offsetY

def rightButtonPressed(event):
    if event.x >= 1000 + offsetX and event.x <= 1000 + offsetX + 150 and event.y >= 325 + offsetY and event.y <= 325 + offsetY + 20:
        global preset
        if preset == 'ms':
            preset = 'ek'
        elif preset == 'ek':
            preset = 'ms'


    for i, tempSpell in enumerate(spells):
        if event.x >= 1000 + offsetX and event.x <= 1000 + offsetX + tempSpell.width and event.y >= 300 + offsetY - (i * 20) and event.y <= 300 + offsetY - (i * 20) + tempSpell.height:
            spells.remove(tempSpell)
    

screen.bind('<Button-1>', buttonPressed)
screen.bind('<Button-3>', rightButtonPressed)

def mouseDragged(event):
    global offsetX
    offsetX = event.x - pressedX
    global offsetY
    offsetY = event.y - pressedY

screen.bind('<B1-Motion>', mouseDragged)

def close(event):
    screen.destroy()

screen.bind('<Escape>', close)

canvas = tk.Canvas(screen, highlightthickness = 0)
canvas.configure(bg='#eee')
canvas.pack(fill=tk.BOTH, expand=True)
canvas.bind('')

def getProcessName():
    try:
        pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
        return psutil.Process(pid[-1]).name()
    except:
        pass

def key_press(key):
    if requireTibia and getProcessName() != 'client.exe':
        return

    if key.name == 'enter':
        global chatOn
        chatOn = not chatOn

    if chatOn:
        return


    if preset == 'ek':
        if key.name == 'f1':
            tempSpell = spell.Spell('utito tempo', 'red', 10000, 2000, type='utito')
        
        if key.name == 'f2':
            tempSpell = spell.Spell('utamo tempo', 'blue', 10000, 2000, type='utito')

        if key.name == 'v' and not keyboard.is_pressed('ctrl'):
            tempSpell = spell.Spell('utani tempo hur', 'green', 4500, type='haste')

        if key.name == 'v' and  keyboard.is_pressed('ctrl'):
            tempSpell = spell.Spell('utani hur', 'green', 32000, 2000, type='haste')

        if key.name == '\'' and keyboard.is_pressed('ctrl'):
            tempSpell = spell.Spell('utura gran', 'green', 60000)

        if key.name == '\'' and not keyboard.is_pressed('ctrl'):
            tempSpell = spell.Spell('exura ico', 'blue', 1000)

        if key.name == '1':
            tempSpell = spell.Spell('exori ico', 'red', 6000, property='attack')

        if key.name == '2':
            tempSpell = spell.Spell('exori hur', 'red', 6000, property='attack')

        if key.name == '3':
            tempSpell = spell.Spell('exori min', 'purple', 6000, property='attack')

        if key.name == '4':
            tempSpell = spell.Spell('exori', 'red', 4000, property='attack')

        if key.name == '5':
            tempSpell = spell.Spell('exori gran', 'orange', 6000, property='attack')

        if key.name == 't':
            tempSpell = spell.Spell('exori mas', 'brown', 8000, property='attack')

        if key.name == 'r':
            tempSpell = spell.Spell('exeta res', 'pink', 4000, 2000)

    if preset == 'ms':
        if key.name == 'r':
            tempSpell = spell.Spell('utamo vita', 'blue', 180000, 15000)
        if key.name == 'v' and  keyboard.is_pressed('ctrl'):
            tempSpell = spell.Spell('utani hur', 'green', 32000, 2000, type='haste')
        if key.name == 'v' and not keyboard.is_pressed('ctrl'):
            tempSpell = spell.Spell('utani gran hur', 'green', 22000, 2000, type='haste')
        if key.name == '1':
            tempSpell = spell.Spell('exori strike', 'brown', 2000, property='attack')
        if key.name == '3':
            tempSpell = spell.Spell('exevo gran vis lux', 'brown', 4000, 2000, property='attack')
        if key.name == '4':
            tempSpell = spell.Spell('exevo vis hur', 'purple', 8000, 2000, property='attack')
        if key.name == '5':
            tempSpell = spell.Spell('exevo gran flam hur', 'red', 4000, 2000, property='attack')
        if key.name == '\'':
            tempSpell = spell.Spell('exura', 'blue', 1000)
        if key.name == 'g':
            tempSpell = spell.Spell('exura gran', 'blue', 1000)
        if key.name == 'f':
            tempSpell = spell.Spell('mana potion', 'black', 1000)
        if key.name == 'l' and  keyboard.is_pressed('alt'):
            tempSpell = spell.Spell('mastermind potion', 'pink', 1000 * 60 * 10)

    if not 'tempSpell' in locals():
        return

    try:
        for s in spells:
            if s.type != '' and s.type == tempSpell.type:
                spells.remove(s)

        spells.remove(tempSpell)
    except:
        pass

    spells.append(tempSpell)

    if tempSpell.property == 'attack':
        global attackCd
        attackCd = spell.Spell('attackCd', 'yellow', 2000, 2000)

keyboard.on_press(key_press)

while True:

    mouseX = pyautogui.position().x
    mouseY = pyautogui.position().y

    if requireTibia and mouseX >= 1000 + offsetX and mouseX <= 1150 + offsetX and mouseY <= 350 + offsetY and mouseY >= 300 - (len(spells) * 20) + offsetY:
        mouseIsOver = True
        hoverCounter += 1
    else:
        mouseIsOver = False
        hoverCounter = 0

    canvas.delete('all')

    if requireTibia and getProcessName() != 'client.exe' and getProcessName() != 'python.exe':
        canvas.update()
        continue


    if not mouseIsOver or hoverCounter >= 100000:
        for i, tempSpell in enumerate(spells):
            tempSpell.draw(canvas, 1000 + offsetX, 300 - (i * 20) + offsetY)

            if tempSpell.timeLeft() <= 0:
                spells.remove(tempSpell)

        canvas.create_rectangle(1000 + offsetX, 325 + offsetY, 1000 + offsetX + 150, 325 + offsetY + 20, fill='white')
        canvas.create_text(1002 + offsetX, 335 + offsetY, fill='black', text='Preset:', anchor='w')
        canvas.create_text(1140 + offsetX, 335 + offsetY, fill='black', text=preset, anchor='e')

        if chatOn:
            canvas.create_rectangle(1000 + offsetX, 345 + offsetY, 1000 + offsetX + 10, 345 + offsetY + 10, fill='red')
        
        canvas.create_rectangle(1000 + 150 - 10 + offsetX, 345 + offsetY, 1000 + 150 + offsetX, 345 + offsetY + 10, fill='blue')

        if attackCd:
            attackCd.draw(canvas, 1000 + offsetX, 320 + offsetY)
            if attackCd.timeLeft() <= 0:
                if attackCd.timeLeft() * 10 % 2 == 0:
                    attackCd.color = 'yellow'
                else:
                    attackCd.color = 'red'

    canvas.update()