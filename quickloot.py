import pyautogui
import time

clickPositions = [
    { 'x': 1022, 'y': 504 },
    { 'x': 936, 'y': 507 },
    { 'x': 872, 'y': 507 },
    { 'x': 1016, 'y': 436 },
    { 'x': 942, 'y': 437 },
    { 'x': 871, 'y': 436 },
    { 'x': 1018, 'y': 372 },
    { 'x': 943, 'y': 370 },
    { 'x': 856, 'y': 361 }
]

def quickLoot():
    global clickPositions
    
    pyautogui.keyDown('shift')
    time.sleep(0.1)

    for position in clickPositions:
        pyautogui.click(x = position['x'], y = position['y'], button = pyautogui.RIGHT)

    pyautogui.keyUp('shift')
    
    return

