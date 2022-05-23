# Explicación Automatización de Vigilancia de PERTES

## Objeto

El objetivo del presente apartado es hacer seguimiento de las principales líneas y convocatorias de los PERTES (Agroalimentario, Economía Circular, ERHA, Nueva Economía de la Lengua, Salud de Vanguardia...)

Para un seguimiento más cómodo, se incorpora una automatización que avisa cuando las líneas y convocatorias de los PERTES han sido nombrados en BOE (las líneas están previamente etiquetadas con los códigos de las órdenes de bases o reales decretos que las regulan). Cuando llegue un nuevo registro a avisos, se notificará a través de mail automático, mediante la regla de automatización Vigilancia PERTE.
A continuación se explica con detalle como ha sido ejecutada la parte de automatización.

## Estructura de tablas

El sistema se compone de 6 tablas que son:

-   BBDD Perte: Esta tabla recoge todas las líneas asociadas a los PERTES. Los registros se concetan con la tabla siguiente a través del campo Código, que es el código de la orden de bases o real decreto que regula cada una de las líneas identificadas en los registros de esta tabla.
-   Avisos: Esta tabla recoge todos el histórico de avisos de las líneas de los PERTES (De todas aquellas etiquetadas con el código de la orden de bases o real decreto). Los registros están conectados con la tabla anterior a través del campo linea_código.
-   Auxiliares:
-   -   PERTE: Enumera los PERTES seguidos
    -   Estado de convocatoria/línea del PERTE: Permite seleccionar si la línea/convocatoria está en estado cerrado, resuelto, próximamente...
    -   Consejería Responsable: Enumera las consejerías de La Rioja. BBDD Perte tiene una columna que identifica cada una de las líneas con la consejería encargada de la misma.
    -   Proyecto PRT: Enumera los proyectos de Plan de Transformación de La Rioja. En el caso de que alguna de las líneas afecte a alguno de los proyectos, esta se etiqueta con el proyecto que corresponda.
Estas tablas están relacionadas de la siguiente forma:

![alt text](https://raw.githubusercontent.com/mcochi/githubactionprueba/main/esquema_tablas.jpg)

 
## Vistas

Se incorpora una Vista por cada uno de los PERTES a dar seguimiento - es una view filtrada de la tabla Objeto:

-   -   PERTE Agroalimentario
    -   PERTE Economía Circular
    -   PERTE ERHA
    -   PERTE Nueva Economía de la Lengua
    -   PERTE Salud de Vanguardia

## Lógica

A continuación se presenta los elementos SW necesarios para la automatización.

Toda la lógica está programada en Python3, y está dividida en 2 ficheros:

-   -   run.py: Contiene toda la lógica de extracción de información del BOE, y la carga de toda la información en coda, en la tabla avisos. Para mayor detalle, ver siguientes apartados
    -   vigilancia_perte.yml: Contiene el archivo de despliegue del job periódico que ejecuta a las 8 de la mañana el script run.py. El job es desplegado directamente en una cuenta de github, a través de la herramienta github actions. Para mayor detalle ver siguientes apartados.

El entorno de ejecución es una container con imagen Python3, que se levante en el entorno que github pone a disposición de los usuarios a través de la herramienta github actions. Para mayor detalle, ver vigilancia_perte.yml
A nivel de SW, destacar los siguientes paquetes:

-   -   Codaio
    -   BeautifulSoup (bs4)
    -   Pandas
    -   json
    -   time
    -   requests
    -   ...

En el siguiente apartado se describen con detalle los ficheros que forman la automatización.
Además de la lógica en python, se incorpora un Lookup en la tabla avisos y en la tabla BBDD Pertes que permite vincularlos entre sí, para poder conectarlas en las vistas.

Además, cuando llega un nuevo registro a avisos, se notifica a través de mail automático, mediante la regla de automatización Vigilancia PERTE. El mail incorpora:
-   Titulo del aviso
 -   Link del aviso
  -   PERTE Asociado
  -   Línea por la que se vincula
   -   Código de la línea con la que se vincula
  

### run.py

El fichero run.pycontiene toda la lógica principal y funciones auxiliares de la automatización.

Su main es el siguiente:
```python
if  __name__  ==  '__main__'  :

 CODIGOS = get_codigos()

  print(CODIGOS)

 avisos =  []

  for CODIGO in CODIGOS:

 data = boe_form_buscar(CODIGO, page_hints, start_date, end_date)

  #print(data)

 soup = BS(data)

 elem = soup.findAll('li', class_ =  "resultado-busqueda")

  #print(elem)

  for i in elem:

 linea_codigo = CODIGO.replace('"','')

 organo = i.h3.text

 titulo = i.p.text.replace("'",  '')

 busqueda = i.find("a", attrs =  {"class":  "resultado-busqueda-link-defecto"})['href']

 referencia = i.find("a", attrs =  {"class":  "resultado-busqueda-link-defecto"})['title'].replace("Ref. ","")  + CODIGO.replace('"','')

 link =  "https://www.boe.es/diario_boe/txt.php?id="  + i.find("a", attrs =  {"class":  "resultado-busqueda-link-defecto"})['title'].replace("Ref. ","")  

 avisos.append([linea_codigo, organo, titulo, busqueda, referencia, link])

  

 df = pd.DataFrame(avisos, columns =  ['linea_codigo',  'organo',  'titulo',  'busqueda',  'referencia',  'link'])

 upload_to_coda(complete_payload(pandas_to_coda(df)))
```
Los pasos que sigue son:

1 - Extracción de los códigos de Órdenes de Bases o Reales Decretos identificados en las líneas etiquetadas en la tabla BBDD PERTE. Todo ello viene encapsulado en la función get_codigos()
```python
 CODIGOS = get_codigos()

  print(CODIGOS)

 avisos =  []
```
  

2- A continuación, se recorren todos los códigos devueltos por la anterior función y se simula una consulta al búscador de BOE mediante la función boe_form_buscar, que devuelve la respuesta del formulario. Esa respuesta - que está en formato html, se parsea para encontrar los elementos resultados de la búsqueda mediante bs4.
```python
  for CODIGO in CODIGOS:

 data = boe_form_buscar(CODIGO, page_hints, start_date, end_date)

  #print(data)

 soup = BS(data)

 elem = soup.findAll('li', class_ =  "resultado-busqueda")
```
3 - Después se recorre cada uno de los resultados encontrados, para extraer la información relevante: identificador en BOE, link, órgano... y se añade a una lista.
```python
  for i in elem:

 linea_codigo = CODIGO.replace('"','')

 organo = i.h3.text

 titulo = i.p.text.replace("'",  '')

 busqueda = i.find("a", attrs =  {"class":  "resultado-busqueda-link-defecto"})['href']

 referencia = i.find("a", attrs =  {"class":  "resultado-busqueda-link-defecto"})['title'].replace("Ref. ","")  + CODIGO.replace('"','')

 link =  "https://www.boe.es/diario_boe/txt.php?id="  + i.find("a", attrs =  {"class":  "resultado-busqueda-link-defecto"})['title'].replace("Ref. ","")  

 avisos.append([linea_codigo, organo, titulo, busqueda, referencia, link])

```  

4 . Finalmente, la lista se transforma en una tabla (DataFrame de pandas) y mediante el wrapper de coda se sube al presente documento a la tabla Avisos.
```python

 df = pd.DataFrame(avisos, columns =  ['linea_codigo',  'organo',  'titulo',  'busqueda',  'referencia',  'link'])

 upload_to_coda(complete_payload(pandas_to_coda(df)))

 ```

Para mayor detalle ver anexo I. [run.py](http://run.py)

### vigilancia_perte.yml

El archivo vigilancia_perte.yml despliega el job de ejecución de la lógica del archivo [run.py](http://run.py) en los servidores que pone a disposición Github, a través de la herramienta Github Actions. GitHub Actions es una plataforma de integración y despliegue continuos (IC/DC) que te permite automatizar tu mapa de compilación, pruebas y despliegue. Puedes crear flujos de trabajo y crear y probar cada solicitud de cambios en tu repositorio o desplegar solicitudes de cambios fusionadas a producción.

La ejecución está montada sobre la cuenta personal de github de Marcos Cochi, en su repositorio público githubactionsprueba.

El contenido del archivo es el siguiente y su ubicación para el desliegue es .github/workflows:
```python
name: vigilancia_perte

on:  

 schedule:

  - cron:  "30 6 * * *"

jobs:  

 build:

 runs-on: ubuntu-latest

 steps:

  - name: checkout repo content

 uses: actions/checkout@v2  

  - name: setup python

 uses: actions/setup-python@v2

 with:

 python-version:  '3.7.7'

  - name: install python packages

 run:  |

 python -m pip install --upgrade pip

 pip install -r requirements.txt

  - name: excute py script

 env:  

 CODA__API__KEY: ${{ secrets.CODA__API__KEY }}

 run: python run.py

 ``` 

A continuación, se explica paso a paso cada una de las configuraciones:
1- Configuración del scheduler: En nuestro caso, el job se ejecutará cada día a las 6 y media de la mañana - 8:30 hora España
```python
on:  

 schedule:

  - cron:  "30 6 * * *"
```

2- Se configura el job para ejecutarse en un contenedor con imagen ubuntu-latest. Se chequea su estado y se instala python 3.7
```python
jobs:  

 build:

 runs-on: ubuntu-latest

 steps:

  - name: checkout repo content

 uses: actions/checkout@v2  

  - name: setup python

 uses: actions/setup-python@v2

 with:

 python-version:  '3.7.7'

  ```

3- Se instala los paquetes de dependencia, se incorporan al entorno los secretos (API_KEY de Coda) y finalmente hace correr [run.py](http://run.py)
```python
 run:  |

 python -m pip install --upgrade pip

 pip install -r requirements.txt

  - name: excute py script

 env:  

 CODA__API__KEY: ${{ secrets.CODA__API__KEY }}

 run: python run.py
```
La ejecución y los logs del job puede ser rápidamente controlado a través de la sección Actions:

![alt-text](https://raw.githubusercontent.com/mcochi/githubactionprueba/main/workflow1.JPG)

![alt-text](https://raw.githubusercontent.com/mcochi/githubactionprueba/main/workflow2.JPG)

Para mayor detalle, ver Anexo II. vigilancia_perte.yml

  

# Anexo I. run.py
```python
import ssl

import requests

import json

from datetime import date, timedelta

from bs4 import BeautifulSoup as BS

from datetime import date, timedelta

import pandas as pd

from codaio import Coda, Document

import os

  

  

page_hints = str(2000)

start_date = date(2020, 1, 1).strftime("%Y-%m-%d")

end_date = date.today().strftime("%Y-%m-%d")

docid = "4spIJTjQaK"

tabid = "grid-CC_O8T0w9s"

API__KEY = os.getenv('CODA__API__KEY')

columncodigos = "c-Geo9KSWqb7"

tabavisosid = "grid-MSXLvpfizV"

collinea_codigo = "c-nmvVaHHenQ"

colorgano = "c-OucIoFLlKg"

coltitulo = "c-tCdI5uHaab"

colbusqueda = "c-oxPjJAPb-y"

colreferencia = "c-LjsYMA9diH"

collink = "c-Rk82guuvAI"

  

def get_codigos():

 if hasattr(ssl, '_create_unverified_context'):

 ssl._create_default_https_context = ssl._create_unverified_context

 url = "https://coda.io/apis/v1/docs/" +docid + "/tables/"+ tabid + "/rows"

 headers = {"Authorization": "Bearer "+ API__KEY, "Content-Type":"Application/json"}

 return list(filter(None, json_extract(requests.get(url=url, headers=headers).json(),columncodigos))) #list(filter(None, CODIGOS))

  

def json_extract(obj, key):

 """Recursively fetch values from nested JSON."""

 arr = []

  

 def extract(obj, arr, key):

 """Recursively search for values of key in JSON tree."""

 if isinstance(obj, dict):

 for k, v in obj.items():

 if isinstance(v, (dict, list)):

 extract(v, arr, key)

 elif k == key:

 arr.append(v)

 elif isinstance(obj, list):

 for item in obj:

 extract(item, arr, key)

 return arr

  

 values = extract(obj, arr, key)

 return values

  

#Ejecución de proyectos de innovación de interés general por grupos operativos de la Asociación Europea para la Innovación en materia de productividad y sostenibilidad agrícolas 

#(AEI-Agri), en el marco delPrograma Nacional de Desarrollo Rural 2014-2022, con fondos procedentes del Instrumentode Recuperación Europeo (EU Next Generation).

# CODIGO : "Real Decreto 169/2018" 

  

#Kit digital

# CODIGO ORDEN DE BASES:'ETD/1498/2021'

#CODIGO = 'ETD/1498/2021'

  

def boe_form_buscar(CODIGO, page_hints, start_date, end_date):

 if hasattr(ssl, '_create_unverified_context'):

 ssl._create_default_https_context = ssl._create_unverified_context

  

 url = ("https://www.boe.es/buscar/boe.php?"

 "campo%5B0%5D=ORI"

 "&dato%5B0%5D%5B1%5D=1"

 "&dato%5B0%5D%5B2%5D=2"

 "&dato%5B0%5D%5B3%5D=3"

 "&dato%5B0%5D%5B4%5D=4"

 "&dato%5B0%5D%5B5%5D=5"

 "&dato%5B0%5D%5BT%5D=T"

 "&operador%5B0%5D=and"

 "&campo%5B1%5D=TIT"

 "&dato%5B1%5D=&operador%5B1%5D=and"

 "&campo%5B2%5D=DEM"

 "&dato%5B2%5D=&operador%5B2%5D=and"

 "&campo%5B3%5D=DOC"

 "&dato%5B3%5D="+ CODIGO.replace("/", "%2F") +

 "&operador%5B3%5D=and"

 "&campo%5B4%5D=NBO"

 "&dato%5B4%5D=&operador%5B4%5D=and"

 "&campo%5B5%5D=NOF"

 "&dato%5B5%5D=&operador%5B5%5D=and"

 "&operador%5B6%5D=and"

 "&campo%5B6%5D=FPU"

 "&dato%5B6%5D%5B0%5D=" + start_date + 

 "&dato%5B6%5D%5B1%5D=" + end_date +

 "&page_hits=" + page_hints +

 "&sort_field%5B0%5D=fpu"

 "&sort_order%5B0%5D=desc"

 "&sort_field%5B1%5D=ori"

 "&sort_order%5B1%5D=asc"

 "&sort_field%5B2%5D=ref"

 "&sort_order%5B2%5D=asc"

 "&accion=Buscar")

 return requests.get(url = url).text

  

def pandas_to_coda(df):

 payload_list = []

 for index, row in df.iterrows():

 linea_codigo = row['linea_codigo']

 organo = row['organo']

 titulo = row['titulo'].replace('"', '')

 busqueda = row ['busqueda']

 referencia = row ['referencia']

 link = row ['link']

 payload_list.append(prepare_payload(linea_codigo, organo, titulo, busqueda, referencia, link))

 return payload_list

  

def prepare_payload(linea_codigo, organo, titulo, busqueda, referencia, link):

 payload = { 

 "cells": [

 {"column": collinea_codigo, "value":  linea_codigo},

 {"column": colorgano, "value":  organo},

 {"column": coltitulo, "value":  titulo},

 {"column": colbusqueda, "value":  busqueda},

 {"column": colreferencia, "value":  referencia},

 {"column": collink, "value":  link},

  

 ]}

 return str(payload).replace("'", "\"").replace("&uacute;","ú").replace("&ntilde;",'ñ')

  

def complete_payload(rows_payload):

 payload = '{"rows":[' +  ','.join(rows_payload)  + '], "keyColumns": [ "'  + colreferencia + '"]}'

 print(payload)

 return json.loads(payload)

  

def upload_to_coda(payload) :

 if hasattr(ssl, '_create_unverified_context'):

 ssl._create_default_https_context = ssl._create_unverified_context

  

 coda = Coda(API__KEY)

 coda.upsert_row(docid,tabavisosid,payload)

  

if __name__ == '__main__' :

 CODIGOS = get_codigos()

 print(CODIGOS)

 avisos = []

 for CODIGO in CODIGOS:

 data = boe_form_buscar(CODIGO, page_hints, start_date, end_date)

 #print(data)

 soup = BS(data)

 elem = soup.findAll('li', class_ = "resultado-busqueda")

 #print(elem)

 for i in elem:

 linea_codigo = CODIGO.replace('"','')

 organo = i.h3.text

 titulo = i.p.text.replace("'", '')

 busqueda = i.find("a", attrs = {"class": "resultado-busqueda-link-defecto"})['href']

 referencia = i.find("a", attrs = {"class": "resultado-busqueda-link-defecto"})['title'].replace("Ref. ","") + CODIGO.replace('"','')

 link = "https://www.boe.es/diario_boe/txt.php?id=" + i.find("a", attrs = {"class": "resultado-busqueda-link-defecto"})['title'].replace("Ref. ","") 

 avisos.append([linea_codigo, organo, titulo, busqueda, referencia, link])

  

 df = pd.DataFrame(avisos, columns = ['linea_codigo', 'organo', 'titulo', 'busqueda', 'referencia', 'link'])

 upload_to_coda(complete_payload(pandas_to_coda(df)))

  ```

# Anexo II. vigilancia_perte.yml
```python
name: vigilancia_perte

on: 

 schedule:

 - cron: "30 6 * * *"

jobs: 

 build:

 runs-on: ubuntu-latest

 steps:

 - name: checkout repo content

 uses: actions/checkout@v2 

 - name: setup python

 uses: actions/setup-python@v2

 with:

 python-version: '3.7.7'

 - name: install python packages

 run: |

 python -m pip install --upgrade pip

 pip install -r requirements.txt

 - name: excute py script

 env: 

 CODA__API__KEY: ${{ secrets.CODA__API__KEY }}

 run: python run.py
```
