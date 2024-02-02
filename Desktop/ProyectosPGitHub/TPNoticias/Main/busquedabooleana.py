from pyparsing import Word, alphas, infixNotation, opAssoc
import pickle

class BusquedaBooleana:
    def __init__(self):
        # Carga el archivo pickle
        with open("indice_invertido_final.pkl", "rb") as indice_file:
            self.indice = pickle.load(indice_file)

            #Cargamos las partes del indice a variables
            self.term_id = self.indice["term_id"]
            self.doc_id = self.indice["doc_id"]
            self.indice_invertido = self.indice["indice_invertido"]

        # Definir los operadores booleanos y las reglas de precedencia
        self.operadores = {
            "AND": set.intersection,
            "OR": set.union,
            "NOT": set.difference,
        }

        #Lista con tupla (operador,operandos,como se asocian estos operadores, de izquierda a derecha)
        self.operadores_binarios = [
            ("AND", 2, opAssoc.LEFT),
            ("OR", 2, opAssoc.LEFT),
        ]

        #Lista con la tupla (operador,operandos,asoc)
        self.operadores_unarios = [
            ("NOT", 1, opAssoc.RIGHT),
        ]

        #Caracteres alfabeticos
        self.termino = Word(alphas)


    def procesar_consulta(self, consulta):
        # Definir la gramática para procesar consultas booleanas
        expresion = infixNotation(
            self.termino,
            self.operadores_unarios + self.operadores_binarios,
            lpar="(",
            rpar=")",
        )

        # Analiza el string para que cumpla con la gramatica
        resultado = expresion.parseString(consulta)

        #Extrae las palabras de la consulta
        def extraer_terminos(exp):
            if isinstance(exp, list):
                terminos = []
                for sub_exp in exp:
                    if sub_exp not in {'AND', 'OR', 'NOT'}:
                        terminos.append(extraer_terminos(sub_exp))
                return terminos
            return exp

        # Extraer términos de la consulta - Convierte el objeto a lista
        return extraer_terminos(resultado.asList())

    def buscar(self, consulta):
        # Procesar la consulta - terminos a buscar
        terminos = self.procesar_consulta(consulta)

        # Se muestra que terminos se buscan
        print("Términos procesados:", terminos)

        # Convierte la estructura anidada de terminos en una lista plana
        def aplanar_terminos(terminos):
            if isinstance(terminos, list):
                return [item for sublist in map(aplanar_terminos, terminos) for item in sublist]
            else:
                return [terminos]

        # Obtener los doc_ids para cada término
        listas_de_documentos = []
        for term in aplanar_terminos(terminos):
            term_id = self.term_id.get(term)
            if term_id is not None:
                if term_id in self.indice_invertido:
                    listas_de_documentos.append(self.indice_invertido[term_id])
                else:
                    print(f"Término '{term}' no encontrado en el índice invertido.")
            else:
                print(f"Término '{term}' no encontrado en el mapeo de términos.")

        # Realizar la operación AND sobre las listas de documentos
        doc_ids_resultantes = set(listas_de_documentos[0]).intersection(*listas_de_documentos[1:])

        # Obtener los documentos correspondientes a los doc_ids resultantes
        documentos_resultantes = []
        for doc_id, mapped_id in self.doc_id.items():
            if mapped_id in doc_ids_resultantes:
                documentos_resultantes.append(doc_id)

        return documentos_resultantes

if __name__ == "__main__":
    busqueda = BusquedaBooleana()

    # Ejemplo de búsqueda
    consulta_ejemplo = "salud OR educacion"
    resultados = busqueda.buscar(consulta_ejemplo)

    print(f"Resultados para la consulta '{consulta_ejemplo}':")
    for resultado in resultados:
        print(resultado)