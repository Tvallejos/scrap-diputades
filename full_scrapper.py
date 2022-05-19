import sys
import simple_scrap
from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup
from load_party import cargar_diputades
import json
import os
import settings
import logging
import re
from typing import List, Dict
from unidecode import unidecode

def get_last_id():
    logging.info(f'obteniendo ultima votacion')

    pure_html = urlopen("https://www.camara.cl/legislacion/sala_sesiones/votaciones.aspx")
    soup_html = BeautifulSoup(pure_html, 'html.parser')

    #opening the results table
    tbody = soup_html.find(id="ContentPlaceHolder1_ContentPlaceHolder1_PaginaContent_pnlVotaciones")
    #getting the last votation
    vot_lin = tbody.find_all("a")
    last_vot = vot_lin[0].get("href").split("=")[1]

    return int(last_vot)

def key_of_diputade(name : str, dips : List[str]) -> int: 
    return next(filter( lambda d: re.search(name,d,re.I) , dips))

def get_diputado_by_name(name : str):
    dips = cargar_diputades('./results/diputades.json')
    dip = key_of_diputade(name,dips.keys())
    return dip,dips[dip]

def parse_boletin(bltn : str) -> str:
    #Proyecto de Resolución N° 
    #OTROS 
    #Proyecto de Resolución N° 
    #Boletín 12495-07 
    return bltn

def process_data_name(name : str) -> str:
    return unidecode(name.lower().replace(":",""))

def process_data(data : str) -> str:
    remove = ['  ','\n','\r']
    for s in remove:
        data = data.replace(s,'')
    return data

def scrap_boletin(vote : Dict[str,str]):
    url = f'https://www.camara.cl/legislacion/sala_sesiones/votacion_detalle.aspx?prmIdVotacion={vote["num_votacion"]}'
    logging.info(f'url_boletin: {url}')
    soup_html = BeautifulSoup(urlopen(url), 'html.parser')
    
    info = soup_html.find(id="info-ficha").find_all("div", {"class": "datos-ficha"})
    totvote = soup_html.find("table").find_all('th')
    numvote = soup_html.find("table").find('tr').find_all('td')
    name = list(info[0].children)
    vote['name'] = process_data(name[1].text + name[3].text)
    logging.info(f'boletin de: {vote["name"]}')
    
    info=info[1:len(info)]
    for datos_ficha in info:
        df = list(datos_ficha.children)
        dname = process_data_name(df[1].text)
        ddata = process_data(df[3].text)
        logging.info(f'dato-ficha: {dname} : {ddata}')
        vote[dname] = ddata

    gral= dict()
    for i in range(len(totvote)):
        gral[unidecode(totvote[i].text.lower())] = process_data(numvote[i].text)
    logging.info(f'votacion general: {gral}')
    vote.update({"voto_general":gral})

    return vote

def string_of_vote_name(name : str, v : Dict):
    vg = v['voto_general']
    sv = f"""{name} votó {v['voto']}
    en {v['name']} {v['sesion']}
    materia: {v['materia']}
    articulo: {v['articulo']}
    tramite: {v['tramite']}
    tipo de votacion: {v['tipo de votacion']}
    quorum: {v['quorum']}
    resultado: {v['resultado']}
    votaciones: 
    a favor: {vg['a favor']} | en contra: {vg['en contra']} | abstencion: {vg['abstencion']} | dispensados: {vg['dispensados']}"""
    return sv

def get_votaciones_by_name(name : str):
    logging.info(f'scrapping votaciones by name: {name}')
    name,dip = get_diputado_by_name(name)
    url = f'https://www.camara.cl/diputados/detalle/votaciones_sala.aspx?prmId={ dip["pagina"] }#ficha-diputados'
    logging.info(f'url boletin: {url}')

    soup_html = BeautifulSoup(urlopen(url), 'html.parser')
    votaciones = soup_html.find_all("tr")
    last_vote = votaciones[1].find_all('td')
    vote = dict()
    if len(last_vote) == 4:
        #vote['boletin'] = parse_boletin(last_vote[0].text)
        fecha,sesion = last_vote[1].text.split('-')
        vote['fecha'] = fecha
        vote['sesion'] = sesion
        vote['voto'] = last_vote[2].text
        vote['num_votacion'] = last_vote[3].find('a')['href'].split('=')[1]
        
        logging.debug(f'fecha: {fecha}\n sesion: {sesion}\nvoto: {vote["voto"]}\n num_votacion: {vote["num_votacion"]}')
        vote = scrap_boletin(vote)
    vs = string_of_vote_name(name, vote)
    logging.info(f'vote string: {vs}')
    return vs

def full_scrap(start_id ,wanted_results, filepath, verbose):
    new_data = []
    if verbose:
        toolbar_width = wanted_results

        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1))


    if wanted_results > 30:
        times = wanted_results//30
        
        for i in range(0, times):
            full_scrap(start_id - 30*i, 30, filepath)
        
        full_scrap(start_id +30*times, wanted_results%30, filepath)

        return True

    n_of_projects = wanted_results
    last_project = start_id
    for project_n in range(last_project, last_project - n_of_projects, -1):
        try:
            link = f"https://www.camara.cl/legislacion/sala_sesiones/votacion_detalle.aspx?prmIdVotacion={project_n}"
            status, project_results, meta = simple_scrap.scrap_web(link, project_n)

            project_dict = dict()
            if status:
                meta.update({"votaciones": project_results})
                new_data.append(meta)
        except urllib.error.HTTPError:
            pass
        
        if verbose:
            sys.stdout.write("-")
            sys.stdout.flush()
    if verbose:
        sys.stdout.write("]\n") 

    old_data = []
    if os.path.isfile(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    
    with open(filepath, 'w+', encoding='utf-8') as outfile:
        json.dump(old_data + new_data, outfile, indent=4, ensure_ascii=False)

    return True

if __name__ == "__main__":
    settings.init()
    last_vote = get_votaciones_by_name('carlos')

    #full_scrap(get_last_id(), 10, "./results/data.json")
