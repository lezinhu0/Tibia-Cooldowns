from textwrap import fill
import time

class Spell:

    width = 150
    height = 20

    def __init__(self, name, color, duration, cooldown = 0, type = '', property = ''):
        self.name = name
        self.color = color
        self.duration = duration
        self.start = self.current_mili_time()
        self.cooldown = cooldown
        self.type = type
        self.property = property

    def __eq__(self, other):
        return self.name == other.name

    def current_mili_time(self):
        return round(time.time() * 1000)

    def timeLeft(self):
        return round((self.duration - (self.current_mili_time() - self.start)) / 1000, 1)

    def draw(self, canvas, x, y):
        if self.name == 'attackCd':
            if self.timeLeft() >= 0:
                canvas.create_rectangle(x, y, x + self.width - (self.width * (self.timeLeft() / (self.duration / 1000))), y + 5, fill=self.color)
            elif self.timeLeft() >= -4:
                canvas.create_rectangle(x, y, x + (self.width), y + 5, fill=self.color)
            return

        
        canvas.create_rectangle(x, y, x + self.width, y + self.height, fill='gray')
        canvas.create_rectangle(x, y, x + (self.width * (self.timeLeft() / (self.duration / 1000))), y + self.height, fill=self.color)

        if ((self.duration / 1000) - self.timeLeft()) < self.cooldown / 1000 and self.duration > self.cooldown:
            canvas.create_rectangle(x, y, x + self.width - (self.width * (self.current_mili_time() - self.start) / self.cooldown), y + self.height, fill='black')

        canvas.create_text(x + 5, y + 9, fill='white', text=self.name, anchor='w')
        canvas.create_text(x + self.width - 5, y + 9, fill='white', text=self.timeLeft() if self.timeLeft() < 1 else round(self.timeLeft(), 0), anchor='e')
        
        