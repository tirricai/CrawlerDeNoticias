import json
import xml.etree.ElementTree as ET
import requests
import os
from bs4 import BeautifulSoup
import time

def guardar_noticias_por_portal(portal, seccion, noticias):
    # Se crea la raíz del documento con la declaración del espacio de nombres
    root = ET.Element("rss", attrib={"version": "2.0", "xmlns:content": "http://purl.org/rss/1.0/modules/content/"})
    channel = ET.SubElement(root, "channel")
    channel_title = ET.SubElement(channel, "title")
    channel_title.text = portal

    #Se itera sobre cada noticia y se obtiene title,link y description
    for noticia in noticias:
        item = ET.SubElement(channel, "item")
        titulo = noticia.find('title').text
        enlace = noticia.find('link').text
        descripcion = noticia.find('description')

        #Compruebo si tiene descripcion / conteido
        if descripcion is not None:
            descripcion = descripcion.text
        else:
            descripcion = "Descripción no disponible"
            
        contenido = noticia.find('content:encoded')
        if contenido is not None:
            contenido = contenido.text
        else:
            contenido = ""

        #Se obtiene fecha, title, link y descripcion y se crean los subelementos
        fecha_publicacion = noticia.find('pubDate').text if noticia.find('pubDate') else "Fecha de publicación no disponible"
        title = ET.SubElement(item, "title")
        title.text = titulo
        link = ET.SubElement(item, "link")
        link.text = enlace
        desc = ET.SubElement(item, "description")
        desc.text = descripcion
        pubDate = ET.SubElement(item, "pubDate")
        pubDate.text = fecha_publicacion

        #Si hay contenido se crea el subelemento content:encoded
        if contenido != "":
            cont = ET.SubElement(item, "content:encoded")
            cont.text = contenido

    #Se crea el tree a partir de la raiz
    tree = ET.ElementTree(root)

    #Se define el path donde se guardaran los xml (con el join se une noticias/portal/seccion)
    path = os.path.join("noticias", portal, seccion)

    #Se asegura que el directorio exista, si no existe, lo creo
    os.makedirs(path, exist_ok=True)

    # Se escribe el archivo XML
    tree.write(os.path.join(path, f"{seccion}.xml"), encoding="utf-8", xml_declaration=True)


# Función para cargar y procesar noticias
def cargar_y_procesar_noticias():
    with open('Main/config.json', 'r') as json_file:
        config = json.load(json_file)

        #Obtengo el par portal - seccion
        for portal, secciones in config.items():
            noticias = []
            if portal == "DEFAULT":
                continue
            
            url_base = secciones.get('url_base')

            #Obtengo el par seccion - url
            for seccion, subseccion_url in secciones.items():
                if seccion in ['url_base']:
                    continue

                #Se unen las url
                url_subseccion = url_base + subseccion_url

                #Se hace el soup
                page = requests.get(url_subseccion)
                soup = BeautifulSoup(page.content, 'lxml-xml')

                #Si no tiene item tiene entry (donde se guardasn las noticias)
                if soup.find('item'):
                    noticias = noticias + soup.find_all('item')
                else:
                    noticias = noticias + soup.find_all('entry')
                    
                guardar_noticias_por_portal(portal, seccion, noticias)

while True:
    cargar_y_procesar_noticias()
    time.sleep(600)