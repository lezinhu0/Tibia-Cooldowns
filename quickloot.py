import pyautogui
import time
import ctypes

def quickLoot(lootPositions):
    pyautogui.keyDown('shift')
    time.sleep(0.05)

    for key in lootPositions:
        position = lootPositions[key]
        ctypes.windll.user32.SetCursorPos(position['x'], position['y'])
        ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0) # left down
        ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0) # left up
        #time.sleep(0.01)

    pyautogui.keyUp('shift')
    
    return

