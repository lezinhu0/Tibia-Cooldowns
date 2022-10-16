import turtle
import time
from webbrowser import get
import spell

def current_mili_time():
    return round(time.time() * 1000)

turtle.speed(0)
turtle.tracer(False)
turtle.hideturtle()

wn = turtle.Screen()
wn.title('Tibia Cooldowns')
wn.bgcolor('gray')
wn.setup(width = 800, height = 600)
wn.tracer(0)

g = turtle.Turtle()
g.hideturtle()
width = 100
height = 20

spells = []

utitoTempo = spell.Spell('utito tempo', 'red', 10000)
spells.append(utitoTempo)

utamoVita = spell.Spell('utamo vita', 'blue', 180000)
spells.append(utamoVita)

utaniTempoHur = spell.Spell('utani tempo hur', 'green', 5000)
spells.append(utaniTempoHur)

while True:

    g.clear()

    for i, tempSpell in enumerate(spells):
        tempSpell.draw(g, 100, i * 20)
        if tempSpell.timeleft() <= 0:
            spells.remove(tempSpell)
            
    wn.update()