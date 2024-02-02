import os
import json
import xml.etree.ElementTree as ET
import spacy
import pickle

nlp = spacy.load("es_core_news_sm")

class BSBI:
    def __init__(self):
        self.term_id= {}
        self.doc_id = {}
        self.indice_invertido = {}
        self.bloque_actual = []
        self.contador_termID = 1
        self.contador_doc_id = 1

    def procesar_texto(self, texto):
        #Separa palabras y lematiza el texto
        palabras = nlp(texto) 
        lemas = []

        #Itera sobre cada palabra, veritifica si es una palabra alfabetica y obtiene su forma lema
        for palabra in palabras:
            if palabra.is_alpha:
                lemas.append(palabra.lemma_)
        return lemas

    def agregar_a_bloque(self, portal, seccion, titulo, fecha_publicacion):

        # Concatena los detalles de la noticia para formar un identificador único
        doc_id = f"{portal}-{seccion}-{titulo}-{fecha_publicacion}"

        #Verifico que no esta en el doc_id - Si no esta, le asigno un id unico y lo incremento
        if doc_id not in self.doc_id:
            self.doc_id[doc_id] = self.contador_doc_id
            self.contador_doc_id += 1

        return self.doc_id[doc_id]

    def agregar_a_indice(self, term, doc_id):
        #Busco el termid del termino pasado por parametro
        term_id = self.term_id.get(term)

        #Si no existe, le asigno un nuevo identificador unico e incremento el contador del termid
        if term_id is None:
            term_id = self.contador_termID
            self.term_id[term] = term_id
            self.contador_termID += 1

        #Si el termID no esta en el indice invertido, creo
        if term_id not in self.indice_invertido:

            #Se crea una nueva entrada para este termino, se crea la lista para asociar los docid
            self.indice_invertido[term_id] = []

        #Una vez que tengo la entrada se agrega el docID a la lista de ese termID
        self.indice_invertido[term_id].append(doc_id)

    def procesar_item(self, portal, seccion, item):
        
        #Obtengo la info que necesito
        titulo = item.find('title').text
        descripcion = item.find('description').text
        fecha_publicacion = item.find('pubDate').text

        #Combino la info recolectada
        texto_completo = f"{titulo} {descripcion} {fecha_publicacion}"

        #Lematizo - devuelve la lista de palabras lematizadas
        lemas = self.procesar_texto(texto_completo)

        #Obtengo el docID
        doc_id = self.agregar_a_bloque(portal, seccion, titulo, fecha_publicacion)

        for palabra in lemas:
            self.agregar_a_indice(palabra, doc_id)

    def parse_next_block(self, portal, seccion, archivo_xml):
        try:
            #Parseo el xml
            tree = ET.parse(archivo_xml)
            root = tree.getroot()

            #Encuentro los items
            for item in root.findall('.//item'):
                #Proceso cada noticia
                self.procesar_item(portal, seccion, item)

        #Catch de excepciones
        except ET.ParseError as e:
            print(f"Error al parsear {archivo_xml}: {e}")

    def construir_indice_completo(self):
        #Itero sobre portales y secciones para obtener los xml (que feos for)
        for portal in config:
            if portal != "DEFAULT":
                for seccion in config[portal]:
                    if seccion != "url_base":
                        path = os.path.join("noticias", portal, seccion)
                        for archivo in os.listdir(path):
                            archivo_path = os.path.join(path, archivo)
                            if os.path.isfile(archivo_path) and archivo.endswith(".xml"):
                                self.parse_next_block(portal, seccion, archivo_path)

        # Guardar el índice invertido usando pickle en modo de escritura binaria
        with open("indice_invertido_final.pkl", "wb") as pickle_file:
            pickle.dump({
                "term_id": self.term_id,
                "doc_id": self.doc_id,
                "indice_invertido": self.indice_invertido
            }, pickle_file)

if __name__ == "__main__":
    with open('Main/config.json', 'r') as json_file:
        config = json.load(json_file)

    bsbi_indexer = BSBI()
    bsbi_indexer.construir_indice_completo()