import requests
from bs4 import BeautifulSoup

def findPlayers(world, levels):
    r = requests.get("https://www.tibia.com/community/?subtopic=worlds&world=" + world[0].upper() + world[1:].lower())
    soup = BeautifulSoup(r.text, features='html.parser')

    characters = []
    for x, row in enumerate(soup.select('.Table2 tr.Odd, .Table2 tr.Even')):
        tempChar = {}

        for index, character in enumerate(row.select('td')):
            if index == 0:
                tempChar['name'] = str(character.select('a[href]')[0].encode_contents()).replace('\\xc2\\xa0', ' ').replace('b\'', '').replace('\'', '')
            elif index == 1:
                tempChar['level'] = int(str(character.encode_contents()).replace('\\xc2\\xa0', ' ').replace('b\'', '').replace('\'', ''))
            elif index == 2:
                tempChar['vocation'] = str(character.encode_contents()).replace('\\xc2\\xa0', ' ').replace('b\'', '').replace('\'', '')
                if tempChar['vocation'].upper() in ['MASTER SORCERER', 'ELITE KNIGHT', 'ELDER DRUID', 'ROYAL PALADIN']:
                    tempChar['premium'] = True
                else:
                    tempChar['premium'] = False

        match = True

        for level in levels.split(','):
            if not (tempChar['level'] >= (int(level) * 0.6667) and tempChar['level'] <= (int(level) / 0.6667)):
                match = False

        if match:
            characters.append(tempChar)

    return characters