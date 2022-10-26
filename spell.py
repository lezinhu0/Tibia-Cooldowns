from audioop import cross
from re import X
import time

class Spell:

    def __init__(self, name, color, duration, cooldown = 0, type = '', property = '', turnCharacter = False, inGamehotkey = None, width = 150, height = 20, crosshair = False, x = 0, y = 0):
        self.name = name
        self.color = color
        self.duration = duration
        self.start = self.current_mili_time()
        self.cooldown = cooldown
        self.type = type
        self.property = property
        self.width = width
        self.height = height
        self.crosshair = crosshair
        self.x = x
        self.y = y
        self.turnCharacter = turnCharacter
        self.inGameHotkey = inGamehotkey

    def __eq__(self, other):
        if other == None:
            return False
            
        return self.name == other.name

    def current_mili_time(self):
        return round(time.time() * 1000)

    def timeLeft(self):
        return round((self.duration - (self.current_mili_time() - self.start)) / 1000, 2)

    def intersects(self, x, y):
        if x >= self.x and x <= self.x + self.width and y >= self.y and y <= self.y + self.height:
            return True

        return False

    def draw(self, canvas):
        if self.name == 'attackCd':
            if self.timeLeft() >= 0:
                canvas.create_rectangle(self.x, self.y, self.x + self.width - (self.width * (self.timeLeft() / (self.duration / 1000))), self.y + self.height, fill=self.color)
            elif self.timeLeft() >= -4:
                canvas.create_rectangle(self.x, self.y, self.x + (self.width), self.y + self.height, fill=self.color)
            return

        if self.name == 'healingCd':
            if self.timeLeft() >= 0:
                canvas.create_rectangle(self.x, self.y, self.x + self.width - (self.width * (self.timeLeft() / (self.duration / 1000))), self.y + self.height, fill=self.color)
            elif self.timeLeft() >= -4:
                canvas.create_rectangle(self.x, self.y, self.x + (self.width), self.y + self.height, fill=self.color)
            return

        canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill='gray')

        canvas.create_rectangle(self.x, self.y, self.x + (self.width * (self.timeLeft() / (self.duration / 1000))), self.y + self.height, fill=self.color)

        if ((self.duration / 1000) - self.timeLeft()) < self.cooldown / 1000 and self.duration > self.cooldown:
            canvas.create_rectangle(self.x, self.y, self.x + self.width - (self.width * (self.current_mili_time() - self.start) / self.cooldown), self.y + self.height, fill='black')

        canvas.create_text(self.x + 5, self.y + 9, fill='white', text=self.name, anchor='w')
        canvas.create_text(self.x + self.width - 5, self.y + 9, fill='white', text=round(self.timeLeft(), 1) if self.timeLeft() < 1 else round(self.timeLeft()), anchor='e')
        
        