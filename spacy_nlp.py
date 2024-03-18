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
punt_matcher=Matcher(nlp.vocab)
# Lista de reglas gramaticales
'''    Artículo + sintagma nominal
    Preposición + sintagma nominal
    Conjunción + frase
    Pronombre + verbo
    Partes de una forma verbal
    Adverbios de negación + verbo
    Preposición + sintagma verbal'''

grammatical_rules = [
    {"label": "component", "pattern": [{"pos": {"in": ["DET"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADP"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["CONJ"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["PRON"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["VERB"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADV"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADP"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"ORTH": "¡"}]},#signos lado izquierdo
    {"label": "component", "pattern": [{"ORTH": "¿"}]}
]

puntuation_rules=[
    {"label": "component", "pattern": [{"ORTH": ","}]},  # Match para coma
    {"label": "component", "pattern": [{"ORTH": "."}]},  # Match para punto
    {"label": "component", "pattern": [{"ORTH": "!"}]}, #signos lado derecho
    {"label": "component", "pattern": [{"ORTH": "?"}]},
    {"label": "component", "pattern": [{"ORTH": ";"}]},
    {"label": "component", "pattern": [{"ORTH": ":"}]}
]
for rule in puntuation_rules:
    punt_matcher.add(rule["label"], [rule["pattern"]])

for rule in grammatical_rules:
    matcher.add(rule["label"], [rule["pattern"]])

def ajustar_duraciones(new_subtitles, margin=0.05):
    for i in range(1, len(new_subtitles) - 1):
        current_subtitle = new_subtitles[i]
        previous_subtitle = new_subtitles[i - 1]
        next_subtitle = new_subtitles[i + 1]

        if current_subtitle.end - current_subtitle.start < srt.timedelta(seconds=1):
            # Verifica si hay espacio para ajustar el inicio y el final
            if (current_subtitle.start - previous_subtitle.end).total_seconds() >= margin and (next_subtitle.start - current_subtitle.end).total_seconds() >= margin:
                # Ajusta el inicio y el final del subtítulo
                current_subtitle.start -= srt.timedelta(seconds=0.2)
                current_subtitle.end += srt.timedelta(seconds=0.3)

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
def puntuation(doc, max_chars, margin):
    
    
    return None
def split_sentence_v3(sentence, max_chars, margin):
    doc = nlp(sentence)

    pun_matches= sorted((start, end) for _, start, end in punt_matcher(doc))

    matches = sorted((start, end) for _, start, end in matcher(doc))#lista de matchs
    '''
    Ejemplo para entender matches:
        'El pulpo es un animal de aspecto bastante extraño que exhibe comportamientos asombrosamente complejos.'
        '0 El 1 pulpo 2 es 3  un 4 animal 5 de 6 aspecto 7 bastante 8 extraño 9 que 10 exhibe 11 comportamientos 12 asombrosamente 13 complejos 14 . 15'
        En esa oracion los matches son : [(1, 2), (8, 10), (9, 10), (11, 12)] que se corres ponden con : 'pulpo' , 'extraño que' , 'que' , 'comportamientos' 
'''

    fragments = []
    

    '''# Si hay solo una coincidencia, dividir en función de esa coincidencia
    if len(matches) == 1000:
        start, end = matches[0]
        length = end - start
        match_duration = duration * (length / len(doc))

        if length <= max_chars + margin and abs(match_duration - min_duration) <= margin:
            fragments.append(doc[start_idx:start].text)
            start_idx = start
        fragments.append(doc[start_idx:].text)
        return fragments'''

    # Si hay más de una coincidencia, elegir las que proporcionen la mejor división
    if len(matches) >= 1:
        suma_acumulativa = calcular_suma_acumulativa(doc.text, max_chars, margin)[:-1]  # Grupos pseudoideales
        # se resta 1 porque el ultimo valor no tiene significado al  ser la ultima palabra
        if(len(suma_acumulativa)==0):#caso linea mayor a max_chars pero menor a max_char+margin
            return [doc.text]
        #creamos una matriz nº matches * nº cortes pseudoideales
        all_distances = np.zeros((len(matches), len(suma_acumulativa)))  # Matriz para almacenar las distancias de cada match con respecto a la suma acumulativa
        all_distances_punt=np.zeros((len(pun_matches), len(suma_acumulativa))) 
        #min_distance = float('inf')
        for idx, (start, _) in enumerate(matches):
            # Se resta 1 en suma porque devuelve la posición de 1 hasta n
            # y en matches las posiciones del match están de 0 hasta n-1
            distances = [abs((suma - 1) - start) for suma in suma_acumulativa]#lista de distancias de 1 matche a n cortes pseudoideal
                
            all_distances[idx] = distances

        for idx, (_, end) in enumerate(pun_matches):
            # Se resta 1 en suma porque devuelve la posición de 1 hasta n
            # y en matches las posiciones del match están de 0 hasta n-1
            distances = [abs((suma - 1) - end) for suma in suma_acumulativa]#lista de distancias de 1 matche a n cortes pseudoideal
                
            all_distances_punt[idx] = distances



        all_distances_t=all_distances.T#ponemos por filas el corte y por columnas los matches para ver cual es el mas ideal
        all_distances_punt_t=all_distances_punt.T
        unique_indices = []

        # Obtener el índice del mejor match para cada columna de all_distances_t
        
        for idx, _ in enumerate(all_distances_t):
            best_match_index = np.argmin(all_distances_t[idx])#argmin devuelve el indice del valor minimo
            best_match_pun_index = np.argmin(all_distances_punt_t[idx])

            min_value_match=all_distances_t[best_match_index]
            min_value_pun_match=all_distances_punt_t[best_match_pun_index]
            min_dist_index=int(np.min([min_value_match,min_value_pun_match]))
            #falta corregir de aqui ao final da funcion.
            matches_final=[]
            if(min_dist_index==best_match_index):
                matches_final=matches
            else:
                matches_final=pun_matches

            index = matches_final[min_dist_index][0]

            if index not in unique_indices:#esta condicion es para asegurarnos de usar el match solo 1 vez
                unique_indices.append(index)
        

        # Convertir la lista de índices únicos a una lista
        best_match_indices = list(unique_indices)

        if len(best_match_indices)==1:
            fragments.append(doc[0:best_match_indices[0]].text+"\n"+doc[best_match_indices[0]:].text)
        else:
            start_idx = 0
            start=0
            while(start_idx+1<len(best_match_indices)):
                if(start==start_idx):
                    fragments.append(doc[start_idx:best_match_indices[start_idx]].text+"\n"
                                     +doc[best_match_indices[start_idx]:best_match_indices[start_idx+1]].text)#
                    start_idx = start_idx+1
                else:    
                    fragments.append(doc[best_match_indices[start_idx]:best_match_indices[start_idx+1]].text+"\n"
                                     +doc[best_match_indices[start_idx+1]:best_match_indices[start_idx+2]].text)#se fragmenta el texto desde donde indica start hasta best_match, este no incluido
                    start_idx = start_idx+2              

            # Añadir el último fragmento
            if(len(best_match_indices)%2==0):
                fragments.append(doc[best_match_indices[start_idx]:].text)

        return fragments
    
    elif len(matches)==0:
        return [doc.text]


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
            lines = split_sentence_v3(text,max_characters,margin)
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

    ajustar_duraciones(new_subtitles)
    print("End formating subs")
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(srt.compose(new_subtitles))


'''def main():
    dividir_lineas_v2("TFG_compartido\How octopuses battle each other _ DIY Neuroscience, a TED series (1080p_24fps_H264-128kbit_AAC).spa.deepgram_nova-2.srt",
                   "TFG_compartido\How octopuses battle each other _ DIY Neuroscience, a TED series (1080p_24fps_H264-128kbit_AAC).spa.deepgram_nova-2_formated.srt")


main()'''
