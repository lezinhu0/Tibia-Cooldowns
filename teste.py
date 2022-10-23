import requests
from bs4 import BeautifulSoup

r = requests.get("https://www.tibiawiki.com.br/wiki/Capacetes")
soup = BeautifulSoup(r.text, features='html.parser')

for index, tr in enumerate(soup.select('#tabelaDPL tr')):
    for td in tr.select('td'):
        print(td.encode_contents())

    if index >= 5:
        break