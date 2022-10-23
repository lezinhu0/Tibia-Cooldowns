import pyautogui
import time
import ctypes

def quickLoot(lootPositions):
    pyautogui.keyDown('shift')
    time.sleep(0.05)

    x = pyautogui.position().x
    y = pyautogui.position().y

    for key in lootPositions:
        position = lootPositions[key]
        ctypes.windll.user32.SetCursorPos(int(position['x']), int(position['y']))
        ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0)

    pyautogui.keyUp('shift')

    ctypes.windll.user32.SetCursorPos(x, y)
    
    return

