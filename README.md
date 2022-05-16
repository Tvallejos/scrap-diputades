# Scrapping de la camara de diputados
WebScrap de la Camara de Diputados de Chile

### Instalación
``` 
$ virtualenv env
$ source env/bin/activate 
$ pip install -r requirements.txt
```

### Correr con
```
source env/bin/activate
python main.py 
```


### FLAGS 
```
    -h, --help   show this help message and exit
    -p PROYECTOS, --proyectos PROYECTOS  Cantidad de proyectos a scrapear
    -i ID, --id ID        id del proyecto inicial para scrapear (opcional) 
    -d , --diputados     Actualiza la informacion de los diputados
    -f FOLDER, --folder FOLDER   path donde guardar los datos
    -v  mostrar progreso
```
