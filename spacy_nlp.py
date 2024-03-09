import spacy,srt,configparser,json,numpy as np
from spacy.tokens import Doc
from spacy.matcher import Matcher
#import concurrent.futures,queue, multiprocessing,logging
#import openai

# Configura tu clave de API de OpenAI

config=configparser.ConfigParser()
config.read('.env')
#openai.api_key=config.get('API_KEYS','CHATGPT_API')

nlp = spacy.load("es_dep_news_trf")
#nlp = spacy.load("es_core_web_sm")
matcher = Matcher(nlp.vocab)

# Lista de reglas gramaticales
'''    Artículo + sintagma nominal
    Preposición + sintagma nominal
    Conjunción + frase
    Pronombre + verbo
    Partes de una forma verbal
    Adverbios de negación + verbo
    Preposición + sintagma verbal'''
'''
grammatical_rules = [
    {"label": "component", "pattern": [{"pos": {"in": ["DET"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADP"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["CONJ"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["PRON"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["VERB"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADV"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADP"]}, "dep": "ROOT"}]},
]'''
grammatical_rules = [
    {"label": "component", "pattern": [{"pos": {"in": ["DET"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADP"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["CONJ"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["PRON"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["VERB"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADV"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADP"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["NOUN"]}, "dep": {"in": ["nsubj", "obj"]}}]},  # Sintagma verbal
    {"label": "component", "pattern": [{"pos": "ADJ"}, {"dep": {"in": ["nsubj", "amod"]}}]},  # Sintagma adjetival
    {"label": "component", "pattern": [{"pos": {"in": ["PRON"]}, "dep": "nsubj"}, {"dep": "ROOT"}]},  # Oración subordinada sustantiva
    {"label": "component", "pattern": [{"pos": {"in": ["PRON"]}, "dep": "nsubj"}, {"pos": "AUX"}, {"pos": "VERB"}]},  # Oración subordinada adjetiva
    {"label": "component", "pattern": [{"ORTH": ","}]},  # Match para coma
    {"label": "component", "pattern": [{"ORTH": "."}]}  # Match para punto
]


for rule in grammatical_rules:
    matcher.add(rule["label"], [rule["pattern"]])



def obtener_longitudes_palabras(texto):
    palabras = texto.split()
    len_palabras = [len(palabra) for palabra in palabras]
    #return json.dumps(palabras_longitudes, ensure_ascii=False)
    return palabras,len_palabras

def agrupar_palabras_por_tamaño(palabras,len_palabras, max_chars, margin):
    grupos = []
    grupo_actual = []
    longitud_actual = 0

    for i,palabra in enumerate(palabras):
        longitud = len_palabras[i]
        if longitud_actual + longitud <= max_chars + margin:
            grupo_actual.append(palabra)
            longitud_actual += longitud
        else:
            grupos.append(grupo_actual)
            grupo_actual = [palabra]
            longitud_actual = longitud

    if grupo_actual:
        grupos.append(grupo_actual)

    return grupos
'''
primera linea: calcular la longitud de cada palabra en la linea de subtitulos. Esto devuelve una lista longitudes y otra lista con las palabras de forma individual
segunda linea: agrupa las palabras por grupos de tamaño maximo max_chars+margin. Esto devuelve una lista de listas donde cada lista tiene las palabras de forma individual
tercera linea: contamos la cantidad de palabras en cada lista
bucle: calcula la suma acumulativa de la cantidad de palabras y devuelve una lista. Ej [9,4] -> [9,13]
'''
def calcular_suma_acumulativa(texto, max_chars, margin):
    palabras, len_palabras = obtener_longitudes_palabras(texto)
    grupos = agrupar_palabras_por_tamaño(palabras, len_palabras, max_chars, margin)
    suma_palabras_por_grupo = [len(grupo) for grupo in grupos]

    suma_acumulativa = []
    suma_temporal = 0

    for num_palabras in suma_palabras_por_grupo:
        suma_temporal += num_palabras
        suma_acumulativa.append(suma_temporal)

    return suma_acumulativa

def split_sentence_v3(sentence, duration, max_chars, min_duration, margin):
    doc = nlp(sentence)
    matches = sorted((start, end) for _, start, end in matcher(doc))#lista de matchs
    '''
    Ejemplo para entender matches:
        'The octopus is a rather strange looking animal that exhibits amazingly complex behaviors.'
        En esa oracion los matches son : [(7, 9), (8, 9), (13,14)] que se corres ponden con : 'looking animal' , 'that' y '.'
'''

    fragments = []
    start_idx = 0

    # Si hay solo una coincidencia, dividir en función de esa coincidencia
    if len(matches) == 1000:
        start, end = matches[0]
        length = end - start
        match_duration = duration * (length / len(doc))

        if length <= max_chars + margin and abs(match_duration - min_duration) <= margin:
            fragments.append(doc[start_idx:start].text)
            start_idx = start
        fragments.append(doc[start_idx:].text)
        return fragments

    # Si hay más de una coincidencia, elegir las que proporcionen la mejor división
    elif len(matches) >= 1:
        suma_acumulativa = calcular_suma_acumulativa(doc.text, max_chars, margin)[:-1]  # Grupos pseudoideales
        # se resta 1 porque el ultimo valor no tiene significado al  ser la ultima palabra
        if(len(suma_acumulativa)==0):#caso linea mayor a max_chars pero menor a max_char+margin
            return [doc.text]
        #creamos una matriz nº matches * nº cortes pseudoideales
        all_distances = np.zeros((len(matches), len(suma_acumulativa)))  # Matriz para almacenar las distancias de cada match con respecto a la suma acumulativa

        min_distance = float('inf')
        for idx, (start, _) in enumerate(matches):
            # Se resta 1 en suma porque devuelve la posición de 1 hasta n
            # y en matches las posiciones del match están de 0 hasta n-1
            distances = [abs((suma - 1) - start) for suma in suma_acumulativa]#lista de distancias de 1 matche a n cortes pseudoideal
                
            all_distances[idx] = distances
            sub_min = min(distances)
            if sub_min < min_distance:
                min_distance = sub_min


        all_distances_t=all_distances.T#ponemos por filas el corte y por columnas los matches para ver cual es el mas ideal

        unique_indices = []

        # Obtener el índice del mejor match para cada columna de all_distances_t
        
        for column_distances in all_distances_t:
            best_match_index = np.argmin(column_distances)
            index = matches[best_match_index][0]
            if index not in unique_indices:#esta condicion es para asegurarnos de usar el match solo 1 vez
                unique_indices.append(index)
        

        # Convertir la lista de índices únicos a una lista
        best_match_indices = list(unique_indices)


        for best_match in best_match_indices:#usamos los match seleccionados para cortar el texto
            fragments.append(doc[start_idx:best_match].text)#se fragmenta el texto desde donde indica start hasta best_match, este no incluido
            start_idx = best_match

        # Añadir el último fragmento
        fragments.append(doc[start_idx:].text)


        return fragments
    
    elif len(matches)==0:
        return [doc.text ]


def dividir_lineas_v2(input_file, output_file):#main function
    print("Formating subs for better reading ....")
    with open(input_file, "r", encoding="utf-8") as file:
        subtitles = list(srt.parse(file.read()))

    new_subtitles = []
    #params
    max_characters=40
    min_duration=1
    margin=8
    for subtitle in subtitles:
        text = subtitle.content
        #print("Subtitle ----- >> "+str(subtitle.index))
        # Aplica el matcher solo si la longitud del subtítulo supera los max_characters
        if len(text) > max_characters:
            lines = split_sentence_v3(text, subtitle.end.total_seconds() - subtitle.start.total_seconds(),max_characters,min_duration,margin)
            #lines=divide_oraciones_with_gpt(text, subtitle.end.total_seconds() - subtitle.start.total_seconds())
        else:
            lines = [text]

        total_words = sum(len(line.split()) for line in lines)
        original_duration = subtitle.end.total_seconds() - subtitle.start.total_seconds()

        for i, line in enumerate(lines):
            line_duration = (len(line.split()) / total_words) * original_duration

            new_subtitle = srt.Subtitle(
                    index=len(new_subtitles) + 1,
                    start=subtitle.start,
                    end=subtitle.start + srt.timedelta(seconds=line_duration),
                    content=line
                )
            new_subtitles.append(new_subtitle)

            subtitle.start = new_subtitle.end

    #ajustar_duraciones(new_subtitles)
    print("End formating subs")
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(srt.compose(new_subtitles))


'''def main():
    dividir_lineas_v2("TFG_compartido\How octopuses battle each other _ DIY Neuroscience, a TED series (1080p_24fps_H264-128kbit_AAC).eng.deepgram_nova-2_transcription.srt",
                   "TFG_compartido\\How octopuses battle each other _ DIY Neuroscience, a TED series (1080p_24fps_H264-128kbit_AAC).eng.deepgram_nova-2_transcription_formated.srt")


main()'''
