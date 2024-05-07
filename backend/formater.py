import spacy,srt,time
from tqdm import tqdm
#from spacy.matcher import Matcher,DependencyMatcher
#from spacy import displacy
#from spacy_rules import puntuation_rules_left,puntuation_rules_right,grammatical_rules_v2
import freeling_parser as freeling
#nlp = spacy.load("es_dep_news_trf")
nlp = spacy.load("es_core_news_sm")

'''
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
    gram_matcher.add(rule["label"], [rule["pattern"]])'''
'''for rule in grammatical_patterns_v2:
    gram_matcher_dependency.add(rule["nombre"], [rule["patron"]])'''


def ajustar_duraciones_v2(new_subtitles, margin=0.05):
    for i in range(len(new_subtitles)):
        subtitle = new_subtitles[i]
        
        # Ajusta el inicio del subtítulo
        new_start = max(subtitle.start - srt.timedelta(seconds=0.2), srt.timedelta(seconds=0))
        if i > 0:
            previous_subtitle = new_subtitles[i - 1]
            if new_start < previous_subtitle.end + srt.timedelta(seconds=margin):
                # Si el solapamiento es menor a 0.2 segundos, ajusta al tiempo entre subtítulos
                if new_start < previous_subtitle.end:
                    new_start = previous_subtitle.end
                else:
                    new_start = previous_subtitle.end + srt.timedelta(seconds=margin)
        
        # Ajusta el final del subtítulo
        new_end = subtitle.end + srt.timedelta(seconds=0.3)
        if i < len(new_subtitles) - 1:
            next_subtitle = new_subtitles[i + 1]
            if new_end > next_subtitle.start - srt.timedelta(seconds=margin):
                # Si el solapamiento es menor a 0.3 segundos, ajusta al tiempo entre subtítulos
                if new_end > next_subtitle.start:
                    new_end = next_subtitle.start
                else:
                    new_end = next_subtitle.start - srt.timedelta(seconds=margin)
        
        subtitle.start = new_start
        subtitle.end = new_end

def split_sentence_v3(sentence,matches):
    doc = nlp(sentence)

    '''pun_matches_left=  [start for _, start, _ in punt_matcher_left(doc)]#signos que se separan por el lado izquierdo
    pun_matches_right=   [end for _, _, end in punt_matcher_right(doc)]#signos que  se separan por el lado derecho
    #los matches de signos tienen preferencia a la hora de separar oraciones
    gram_matches =  [start for _, start,_ in gram_matcher(doc)]#lista de matchs gramaticales'''

    #mt=cervantes.process_text(doc.text)
    #matches=[]
    #matches.extend(mt)
    #matches.extend(pun_matches_left+pun_matches_right+gram_matches)
    #sorted_matches=sorted(list(set(matches)))
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
        for index in matches:
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
def dividir_lineas_v2(subtitles):#main function
    print("Formating subs for better reading ....")
    '''with open(input_file, "r", encoding="utf-8") as file:
        subtitles = list(srt.parse(file.read()))'''
    info_file=[]
    new_subtitles = []
    #params
    max_characters=40
    margin=8

    for subtitle in tqdm(subtitles):
        text = subtitle.content
        text_len=sum(1 for char in text if ord(char) < 128)
        with open("info_spacy.txt","a",encoding="utf-8") as info:
                info.write("Before freeling")
        time.sleep(2)
        matches=freeling.matches_freeling(text)
        with open("info_spacy.txt","a",encoding="utf-8") as info:
                info.write("Post freeling")
        time.sleep(2)
        if text_len >= max_characters+margin:
            lines,info = split_sentence_v3(text,matches)  
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

    ajustar_duraciones_v2(new_subtitles)
    #print("End formating subs")
    '''with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(srt.compose(new_subtitles))
    with open("info_spacy.json","w",encoding="utf-8") as info:
        info.write(json.dumps(info_file, indent=4))'''
    return new_subtitles

'''debug_spacy=False
if debug_spacy==True:
    def main():
        import time
        start_time=time.time()
        srt_file="TFG_compartido/[DKB] Yoru no Kurage wa Oyogenai  - S01E01 [1080p][HEVC x265 10bit].es.srt"
        with open(srt_file, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
        subtitulos = list(srt.parse(contenido))
        
        dividir_lineas_v2(subtitulos)
        end_time=time.time()
        print("Tiempo total : "+str((end_time-start_time)/60)+" minutos") 

    main()'''


