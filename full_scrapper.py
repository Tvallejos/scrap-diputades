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
from typing import List

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
    return dips[dip]

def get_votaciones_by_name(name : str):
    dip = get_diputado_by_name(name)
    url = f'https://www.camara.cl/diputados/detalle/votaciones_sala.aspx?prmId={ dip["Pagina"] }#ficha-diputados'

    # TODO SCRAP this url
    
    soup_html = BeautifulSoup(urlopen(url), 'html.parser')
    return

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
    get_votaciones_by_name('carlos')
    full_scrap(get_last_id(), 10, "./results/data.json")
