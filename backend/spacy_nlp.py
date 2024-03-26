import spacy,srt,configparser,json,numpy as np
from tqdm import tqdm
from spacy.matcher import Matcher,DependencyMatcher
from spacy import displacy
from backend.spacy_rules import puntuation_rules_left,puntuation_rules_right,grammatical_rules_v2
#import concurrent.futures,queue, multiprocessing,logging
#import openai

# Configura tu clave de API de OpenAI

config=configparser.ConfigParser()
config.read('.env')

nlp = spacy.load("es_dep_news_trf")


gram_matcher= Matcher(nlp.vocab)
#gram_matcher_dependency= DependencyMatcher(nlp.vocab)
punt_matcher_left=Matcher(nlp.vocab)
punt_matcher_right=Matcher(nlp.vocab)
#https://spacy.io/usage/rule-based-matching
#https://spacy.io/usage/rule-based-matching#dependencymatcher

for rule in puntuation_rules_left:
    punt_matcher_left.add(rule["label"], [rule["pattern"]])

for rule in puntuation_rules_right:
    punt_matcher_right.add(rule["label"], [rule["pattern"]])

for rule in grammatical_rules_v2:
    gram_matcher.add(rule["label"], [rule["pattern"]])
'''for rule in grammatical_patterns_v2:
    gram_matcher_dependency.add(rule["nombre"], [rule["patron"]])'''

def ajustar_duraciones(new_subtitles, margin=0.05):
    for i in range(1, len(new_subtitles) - 1):
        current_subtitle = new_subtitles[i]
        previous_subtitle = new_subtitles[i - 1]
        next_subtitle = new_subtitles[i + 1]

        if current_subtitle.end - current_subtitle.start < srt.timedelta(seconds=1):
            # Verifica si hay espacio para ajustar el inicio y el final
            if (current_subtitle.start - previous_subtitle.end).total_seconds() >= margin and (next_subtitle.start - current_subtitle.end).total_seconds() >= margin:
                # Ajusta el inicio y el final del subtítulo
                current_subtitle.start -= srt.timedelta(seconds=0.2)#al principio
                current_subtitle.end += srt.timedelta(seconds=0.3)#al final

def split_sentence_v3(sentence):
    doc = nlp(sentence)

    pun_matches_left=  [start for _, start, _ in punt_matcher_left(doc)]#signos que se separan por el lado izquierdo
    pun_matches_right=   [end for _, _, end in punt_matcher_right(doc)]#signos que  se separan por el lado derecho
    #los matches de signos tienen preferencia a la hora de separar oraciones
    gram_matches =  [start for _, start,_ in gram_matcher(doc)]#lista de matchs gramaticales
    #start_indices =  gram_matcher_dependency(doc)
    #displacy.serve(doc, style="dep")

    matches=[]
    matches.extend(pun_matches_left+pun_matches_right+gram_matches)
    sorted_matches=sorted(list(set(matches)))
    info={"sentence":sentence,"matches":[]}
    '''
    Ejemplo para entender matches:
        'El pulpo es un animal de aspecto bastante extraño que exhibe comportamientos asombrosamente complejos.'
        '0 El 1 pulpo 2 es 3  un 4 animal 5 de 6 aspecto 7 bastante 8 extraño 9 que 10 exhibe 11 comportamientos 12 asombrosamente 13 complejos 14 . 15'
        En esa oracion los matches son : [(1, 2), (8, 10), (9, 10), (11, 12)] que se corres ponden con : 'pulpo' , 'extraño que' , 'que' , 'comportamientos' 
'''

    fragments = []

    # Si hay más de una coincidencia, elegir las que proporcionen la mejor división
    if len(matches) >= 1:
        match_index=[]
        min=22
        aux=0
        for index in sorted_matches:
            tt=doc[aux:index].text
            long=len(tt)
            if(long > min and len(doc[index:].text)>min ):#se añañde un indice siempre que sea de longitud minima y el texto restante sea mayor al minimo
                match_index.append(index)
                aux=index

        #match_index=match_index[:-1]#quitamos el ultimo indice, en caso de que el ultimo indice sea añadido significa que tiene un fragmento de texto inferior a 22 caracteres
        info["matches"]= match_index

        if len(match_index)==1:#agrupamos de 2 en 2 lineas
            fragments.append(doc[0:match_index[0]].text+"\n"+doc[match_index[0]:].text)
        elif(len(match_index)==0):
            fragments.append(doc.text)
        else:
            start_idx = 0
            
            while(start_idx+1<len(match_index)):
                if(0==start_idx):
                    fragments.append(doc[start_idx:match_index[start_idx]].text+"\n"
                                     +doc[match_index[start_idx]:match_index[start_idx+1]].text)#
                    start_idx = start_idx+1
                elif(start_idx+2==len(match_index)):
                    fragments.append(doc[match_index[start_idx]:match_index[start_idx+1]].text+"\n"
                                     +doc[match_index[start_idx+1]:].text)
                    start_idx = start_idx+2
                else:    
                    fragments.append(doc[match_index[start_idx]:match_index[start_idx+1]].text+"\n"
                                     +doc[match_index[start_idx+1]:match_index[start_idx+2]].text)#se fragmenta el texto desde donde indica start hasta best_match, este no incluido
                    start_idx = start_idx+2              

            # Añadir el último fragmento
            if(len(match_index)%2==0):
                fragments.append(doc[match_index[start_idx]:].text)
        return fragments,info
    elif len(matches)==0:
        return [doc.text],info

###################################################################################
def dividir_lineas_v2(input_file, output_file):#main function
    print("Formating subs for better reading ....")
    with open(input_file, "r", encoding="utf-8") as file:
        subtitles = list(srt.parse(file.read()))
    info_file=[]
    new_subtitles = []
    #params
    max_characters=40
    min_duration=1
    margin=8
    for subtitle in tqdm(subtitles):
        text = subtitle.content
        #print("Subtitle ----- >> "+str(subtitle.index))
        # Aplica el matcher solo si la longitud del subtítulo supera los max_characters
        if len(text) > max_characters+margin:
            lines,info = split_sentence_v3(text)
            info_file.append(info)
            #lines=divide_oraciones_with_gpt(text, subtitle.end.total_seconds() - subtitle.start.total_seconds())
        else:
            lines = [text]

        #total_words = sum(len(line.split()) for line in lines)
        total_chars= sum(len(line) for line in lines) 
        original_duration = subtitle.end.total_seconds() - subtitle.start.total_seconds()

        for i, line in enumerate(lines):
            line_duration = (len(line) / total_chars) * original_duration

            new_subtitle = srt.Subtitle(
                    index=len(new_subtitles) + 1,
                    start=subtitle.start,
                    end=subtitle.start + srt.timedelta(seconds=line_duration),
                    content=line
                )
            new_subtitles.append(new_subtitle)

            subtitle.start = new_subtitle.end

    ajustar_duraciones(new_subtitles)
    #print("End formating subs")
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(srt.compose(new_subtitles))
    with open("info_spacy.json","w",encoding="utf-8") as info:
        info.write(json.dumps(info_file, indent=4))

debug_spacy=False
if debug_spacy==True:
    def main():
        import time
        start_time=time.time()
        dividir_lineas_v2("TFG_compartido/Avalanches_ Unpredictable, Inevitable, Fatal _ Deadly Disasters _ Free Documentary (192kbit_AAC).spa.deepgram_nova-2.srt",
                    "TFG_compartido/Avalanches_ Unpredictable, Inevitable, Fatal _ Deadly Disasters _ Free Documentary (192kbit_AAC).spa.deepgram_nova-2_formated.srt")
        end_time=time.time()
        print("Tiempo total : "+str((end_time-start_time)/60)+" minutos") 

    main()


#funciones no utilizadas
#dentro de split_sentence_v3      
''' suma_acumulativa = calcular_suma_acumulativa(doc.text, max_chars, margin)[:-1]  # Grupos pseudoideales
        # se resta 1 porque el ultimo valor no tiene significado al ser la ultima palabra
        if(len(suma_acumulativa)==0):#caso linea mayor a max_chars pero menor a max_char+margin
            return [doc.text],info
        
        #creamos una matriz nº matches * nº cortes pseudoideales
        all_distances=np.zeros(( len(suma_acumulativa),len(matches)))
        for idx, l in enumerate(suma_acumulativa):
            # Se resta 1 en suma porque devuelve la posición de 1 hasta n
            # y en matches las posiciones del match están de 0 hasta n-1
            distances = [abs((l - 1) - match) for match in matches]#lista de distancias de 1 matche a n cortes pseudoideal
                
            all_distances[idx] = distances

        best_match_indices = []

        # Obtener el índice del mejor match para cada columna de all_distances
        #AQUI HAY QUE APLICAR REGLAS DE LONGITUD MINIMA DEL SEGMENTO Y MATCH_DIST < MAX_DIST_TO_PSEUDOCORTE
        for idx, _ in enumerate(all_distances):
            best_match_index = np.argmin(all_distances[idx])#argmin devuelve el indice del valor minimo

            index_space_sentence = matches[best_match_index]

            if index_space_sentence not in best_match_indices:#esta condicion es para asegurarnos de usar el match solo 1 vez
                best_match_indices.append(index_space_sentence)

        info["matches"]= best_match_indices
        ################################
        #intentaremos agrupar las lineas de 2 en 2 de ser posible
        if len(best_match_indices)==1:
            fragments.append(doc[0:best_match_indices[0]].text+"\n"+doc[best_match_indices[0]:].text)
        else:
            start_idx = 0
            
            while(start_idx+1<len(best_match_indices)):
                if(0==start_idx):
                    fragments.append(doc[start_idx:best_match_indices[start_idx]].text+"\n"
                                     +doc[best_match_indices[start_idx]:best_match_indices[start_idx+1]].text)#
                    start_idx = start_idx+1
                elif(start_idx+2==len(best_match_indices)):
                    fragments.append(doc[best_match_indices[start_idx]:best_match_indices[start_idx+1]].text+"\n"
                                     +doc[best_match_indices[start_idx+1]:].text)
                    start_idx = start_idx+2
                else:    
                    fragments.append(doc[best_match_indices[start_idx]:best_match_indices[start_idx+1]].text+"\n"
                                     +doc[best_match_indices[start_idx+1]:best_match_indices[start_idx+2]].text)#se fragmenta el texto desde donde indica start hasta best_match, este no incluido
                    start_idx = start_idx+2              

            # Añadir el último fragmento
            if(len(best_match_indices)%2==0):
                fragments.append(doc[best_match_indices[start_idx]:].text)

        return fragments,info'''
#antes estas funciones servian
'''def obtener_longitudes_palabras(texto):
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
#primera linea: calcular la longitud de cada palabra en la linea de subtitulos. Esto devuelve una lista longitudes y otra lista con las palabras de forma individual
#segunda linea: agrupa las palabras por grupos de tamaño maximo max_chars+margin. Esto devuelve una lista de listas donde cada lista tiene las palabras de forma individual
#tercera linea: contamos la cantidad de palabras en cada lista
#bucle: calcula la suma acumulativa de la cantidad de palabras y devuelve una lista. Ej [9,4] -> [9,13]
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

    return suma_acumulativa'''