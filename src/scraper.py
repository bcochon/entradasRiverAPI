import requests
from bs4 import BeautifulSoup
from utils import merge_lists

RIVER_URL = 'https://www.cariverplate.com.ar/'
cache_noticias = []
cache_partidos = []

class Entradas:
    def __init__(self, noticia):
        self.noticia = noticia
        self.date = self.find_date(noticia.url)

    def find_date(self, url):
        ...

class Partido:
    def __init__(self, vs: str, torneo: str, date: str, entradas: Entradas = None):
        self.vs = vs
        self.torneo = torneo
        self.date = date
        self.entradas = entradas

class Noticia:
    def __init__(self, title: str, description: str, url: str):
        self.title = title
        self.description = description
        self.url = url
        self.partido = self.fetch_partido(title, description)

    def __str__(self):
        return f'{self.title}\n{self.url}\n{self.description}'
    
    def fetch_partido(self):
        if 'venta de entradas' not in self.title.lower():
            return None
        self.entradas = Entradas(self)
        return None


def build_noticias(soups: list[BeautifulSoup]) -> list[Noticia]:
    result = []
    for s in soups:
        title = s.a.string
        description = s.p.string
        url = RIVER_URL + s.a['href']
        result.append(Noticia(title, description, url))
    return result

def build_partidos(soups: list[BeautifulSoup]) -> list[Partido]:
    result = []
    for s in soups:
        soup_partido = s.find('div', class_='d_calendario')
        vs = soup_partido.b.get_text().replace('River Plate', '').replace('vs.', '').strip()
        torneo = soup_partido.p.strong.string
        date = soup_partido.p.get_text().replace(torneo, '').replace('•', '').strip()
        result.append(Partido(vs, torneo, date))
    return result

def scrap_noticias():
    info = requests.get(RIVER_URL+'noticias-de-entradas')
    soup = BeautifulSoup(info.content, 'html.parser')
    try:
        soup_rows = soup.find('section', id='principal').find_all('div', class_='row')[1:]
        first_row = soup_rows[0].find_all('figure')
        if first_row[0] == cache_noticias[0]:
            return cache_noticias
        second_row_columns = soup_rows[1].find_all('div', class_='col-lg-6 col-md-6 col-xs-12')
        second_row = merge_lists(second_row_columns[0].find_all('figure'), second_row_columns[1].find_all('figure'))
        cache_noticias = first_row + second_row
    except Exception as e:
        print(e)
    return cache_noticias

def scrap_partidos():
    info = requests.get(RIVER_URL+'calendario-de-partidos')
    soup = BeautifulSoup(info.content, 'html.parser')
    try:
        cache_partidos = soup.find('div', id='caledario').find('div', class_='calendario').find_all('li')
    except Exception as e:
        print(e)
    return cache_partidos

def get_noticias(number: int = 10) -> list[Noticia]:
    noticias = scrap_noticias()
    return build_noticias(noticias[:number])

def get_partidos(number: int = 30) -> list[Partido]:
    partidos = scrap_partidos()
    return build_partidos(partidos[:number])

if __name__ == '__main__':
    # [print(noticia, '\n') for noticia in get_noticias(10)]
    get_partidos()