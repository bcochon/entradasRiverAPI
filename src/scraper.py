import requests
import schedule
import logging
import logging.config
from bs4 import BeautifulSoup
from datetime import datetime
from utils import merge_lists, get_date, format_date

logging.config.fileConfig('log.conf')
logger = logging.getLogger('RiverScraper')

RIVER_URL = 'https://www.cariverplate.com.ar/'
DATE_FORMAT = '%x %X'
cache_noticias = []
cache_partidos = []
reload_partidos = False

def build_noticia(title, description, url) -> dict:
    return {
        'title' : title,
        'description' : description,
        'url' : url,
    }

def build_noticias(soups: list[BeautifulSoup]) -> list[dict]:
    result = []
    for s in soups:
        title = s.a.string
        description = s.p.string
        url = RIVER_URL + s.a['href']
        result.append(build_noticia(title, description, url))
    return result

def find_entradas(vs: str, date: datetime) -> None | dict:
    noticias = build_noticias(cache_noticias[:6])
    for noticia in noticias:
        title = noticia['title'].lower()
        date_noticia = get_date(noticia['description'])
        if ('venta de entradas' in title) and (vs.lower() in title) and (date.day == date_noticia.day) and (date.month == date_noticia.month):
            return {
                'url' : noticia['url']
            }
    return None

def build_partido(vs: str, torneo: str, date_string: str) -> dict:
    date = format_date(date_string)
    return {
        'vs' : vs,
        'torneo' : torneo,
        'date' : date.strftime(DATE_FORMAT),
        'entradas' : find_entradas(vs, date)
    }

def build_partidos(soups: list[BeautifulSoup]) -> list[dict]:
    result = []
    for s in soups:
        soup_partido = s.find('div', class_='d_calendario')
        vs = soup_partido.b.get_text().replace('River Plate', '').replace('vs.', '').strip()
        torneo = soup_partido.p.strong.string
        date = soup_partido.p.get_text().replace(torneo, '').replace('•', '').strip()
        result.append(build_partido(vs, torneo, date))
    return result

def scrap_noticias() -> list[BeautifulSoup]:
    logger.info('Obteniendo noticias de entradas...')
    info = requests.get(RIVER_URL+'noticias-de-entradas')
    soup = BeautifulSoup(info.content, 'html.parser')
    global cache_noticias
    global reload_partidos
    try:
        soup_rows = soup.find('section', id='principal').find_all('div', class_='row')[1:]
        first_row = soup_rows[0].find_all('figure')
        if len(cache_noticias) and first_row[0] == cache_noticias[0]:
            logger.info('No hay nuevas noticias')
            reload_partidos = False
            return cache_noticias
        logger.info('Nuevas noticias detectadas')
        second_row_columns = soup_rows[1].find_all('div', class_='col-lg-6 col-md-6 col-xs-12')
        second_row = merge_lists(second_row_columns[0].find_all('figure'), second_row_columns[1].find_all('figure')) 
        cache_noticias = first_row + second_row
        reload_partidos = True
    except Exception as e:
        logger.error(e)
    return cache_noticias

def scrap_partidos() -> list[BeautifulSoup] | None:
    info = requests.get(RIVER_URL+'calendario-de-partidos')
    soup = BeautifulSoup(info.content, 'html.parser')
    try:
        return soup.find('div', id='caledario').find('div', class_='calendario').find_all('li')
    except Exception as e:
        logger.error(e)
    return None

def retrieve_noticias():
    noticias = scrap_noticias()
    if reload_partidos:
        retrieve_partidos()
    return noticias

def get_noticias(number: int = 10) -> list[dict]:
    noticias = retrieve_noticias()
    return build_noticias(noticias[:number])

def retrieve_partidos() -> list[dict]:
    logger.info('Obteniendo partidos según calendario...')
    partidos = scrap_partidos()
    if partidos:
        global cache_partidos
        cache_partidos = build_partidos(partidos)
    global reload_partidos
    reload_partidos = False
    return cache_partidos

def get_partidos(number: int = 30)  -> list[dict]:
    schedule.run_pending
    return cache_partidos

if __name__ == '__main__':
    noticias = get_noticias(10)
    for noticia in noticias:
        print(noticia)
else:
    retrieve_noticias()
    schedule.every(2).hours.do(retrieve_partidos)