import ssl
import requests
import json
from datetime import date, timedelta
from bs4 import BeautifulSoup as BS
from datetime import date, timedelta
import pandas as pd
from codaio import Coda, Document
import urllib.parse
import os
from urllib3 import poolmanager


page_hints = str(2000)
start_date = date(2020, 1, 1).strftime("%Y-%m-%d")
end_date = date.today().strftime("%Y-%m-%d")
docid = "VP3Wn5wzKj"
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
# prueba

class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)

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
  #if hasattr(ssl, '_create_unverified_context'):
  #    ssl._create_default_https_context = ssl._create_unverified_context
  print('€€€€€€€€€')
  print(CODIGO)
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
        "&dato%5B3%5D="+ urllib.parse.quote(CODIGO.replace('“','"').replace('”','"').replace('\n',' ')) + 
        #"&dato%5B3%5D=Resoluci%C3%B3n+de+5+de+septiembre+de+2019+de+la+Secretaria+de+Estado+de+energ%C3%ADa"
        "&operador%5B3%5D=and"
        "&campo%5B4%5D=NBO"
        "&dato%5B4%5D=&operador%5B4%5D=and"
        "&campo%5B5%5D=NOF"
        "&dato%5B5%5D=&operador%5B5%5D=and"
        "&operador%5B6%5D=and"
        "&campo%5B6%5D=FPU"
        #"&dato%5B6%5D%5B0%5D=" + start_date + 
        "&dato%5B6%5D%5B0%5D="
        #"&dato%5B6%5D%5B1%5D=" + end_date +
        "&dato%5B6%5D%5B1%5D="
        #"&page_hits=" + page_hints +
        "&page_hits="
        "&sort_field%5B0%5D=fpu"
        "&sort_order%5B0%5D=desc"
        "&sort_field%5B1%5D=ori"
        "&sort_order%5B1%5D=asc"
        "&sort_field%5B2%5D=ref"
        "&sort_order%5B2%5D=asc"
        "&accion=Buscar")
  print(url)
  session = requests.session()
  session.mount('https://', TLSAdapter())
  res = session.get(url)
  return res.text

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
