import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
from os.path import exists
import os
import logging

def cargar_diputados(filepath):
    results = filepath.split('/')[0]
    dir_exists = exists(results)
    if dir_exists: 
        log.info(f'filepath: {filepath} ya existia')
        return True

    datos = dict()
    log.info('scrapeando diputades')
    pure_html = urlopen('https://www.camara.cl/diputados/diputados.aspx')
    soup_html = BeautifulSoup(pure_html, 'html.parser')

    diputados = soup_html.find_all('article', {'class': 'grid-2'})

    for diputado in diputados:
        datos_diputado = dict()
        name =  diputado.find('h4').find('a').string
        log.debug(f'procesando diputade: {name}')
        distr_nd_party = diputado.find_all('p')
        for k in distr_nd_party:
            raw_data = k.string.split(':')
            datos_diputado.update({raw_data[0]:raw_data[1]})
        
        mail = diputado.find('a', {'class':'contacto'})
        mail = mail.get('href').replace('mailto:', '').replace('?subject=Consulta', '')

        datos_diputado.update({'Correo': mail})
        pag = diputado.find('a')['href'].split('=')[1]
        datos_diputado.update({'Pagina':pag})

        datos.update({name: datos_diputado})
    
    os.makedirs(results)
    log.info(f'creando directorio {results}')
    with open(filepath, 'w', encoding='utf-8') as outfile:
        log.info(f'volcando datos en {filepath}')
        json.dump(datos, outfile, indent=4, ensure_ascii=False)

    return True


if __name__ == "__main__":
    fmt = "[ %(funcName)0s() ] %(message)s"
    logging.basicConfig(level=logging.INFO,format=fmt)
    log = logging.getLogger()
    cargar_diputados('results/diputados.json')