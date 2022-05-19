import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
#from os.path import exists
import os
import logging
import settings 


def cargar_diputades(filepath):
    with open(scrap_diputades(filepath),'r', encoding='utf-8') as dip:
        return json.load(dip)

def scrap_diputades(filepath):
    results = filepath.split('/')[1]
    if os.path.exists(results):
        logging.info(f'filepath: {filepath} ya existia')
        return filepath

    datos = dict()
    logging.info('scrapeando diputades')
    pure_html = urlopen('https://www.camara.cl/diputados/diputados.aspx')
    soup_html = BeautifulSoup(pure_html, 'html.parser')

    diputados = soup_html.find_all('article', {'class': 'grid-2'})

    for diputado in diputados:
        datos_diputado = dict()
        name =  diputado.find('h4').find('a').string
        logging.debug(f'procesando diputade: {name}')
        distr_nd_party = diputado.find_all('p')
        for k in distr_nd_party:
            raw_data = k.string.split(':')
            datos_diputado[raw_data[0]] = raw_data[1]
        
        mail = diputado.find('a', {'class':'contacto'}) \
            .get('href').replace('mailto:', '').replace('?subject=Consulta', '')

        datos_diputado["correo"] = mail
        logging.debug(f'correo: {mail}')
        pag = diputado.find('a')['href'].split('=')[1]
        datos_diputado["pagina"] = pag
        logging.debug(f'id pagina: {pag}')

        datos.update({name: datos_diputado})
    
    os.makedirs(results)
    logging.info(f'creando directorio {results}')
    with open(filepath, 'w', encoding='utf-8') as outfile:
        logging.info(f'volcando datos en {filepath}')
        json.dump(datos, outfile, indent=4, ensure_ascii=False)

    return filepath

if __name__ == "__main__":
    settings.init()
    scrap_diputades('./results/diputades.json')