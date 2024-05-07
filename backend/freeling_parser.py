import json,spacy,requests,time 
from spacy_rules import puntuation_rules_left,puntuation_rules_right
from spacy.matcher import Matcher

#backend_freeling='http://localhost:5002/morfo'
backend_freeling='http://freeling:5002/morfo'

nlp = spacy.load("es_core_news_sm")
punt_matcher_left=Matcher(nlp.vocab)
punt_matcher_right=Matcher(nlp.vocab)

for rule in puntuation_rules_left:
    punt_matcher_left.add(rule["label"], [rule["pattern"]])

for rule in puntuation_rules_right:
    punt_matcher_right.add(rule["label"], [rule["pattern"]])

#
def parser(json_obj,sentence):
    data=json.loads(json_obj)
    doc = nlp(sentence)
    pun_matches_left=  [start for _, start, _ in punt_matcher_left(doc)]#signos que se separan por el lado izquierdo
    pun_matches_right=   [end for _, _, end in punt_matcher_right(doc)]#signos que  se separan por el lado derecho
    match=[]
    match.extend(pun_matches_left+pun_matches_right)
    
    cont=0
    for a in data:
        for token in a["tokens"]:
            morfo=token['analysis'][0]['tag']
            if str(morfo).startswith(('C','SP')):#C significa conjuncion y S significa preposicion   https://freeling-user-manual.readthedocs.io/en/v4.2/tagsets/tagset-es/
                with open("info_spacy.txt","a",encoding="utf-8") as info:
                    info.write("Func parser inside 2 for parser\n")
                time.sleep(2)
                match.append(cont)
                with open("info_spacy.txt","a",encoding="utf-8") as info:
                    info.write("Func parser inside 2 for parser after match append cont\n")
                time.sleep(2)
            cont+=1
    '''with open("info_spacy.txt","a",encoding="utf-8") as info:
        info.write("Func parser before sorted(List(Set()))\n")
    time.sleep(2)'''
    sorted_matches=sorted(list(set(match)))
    return sorted_matches


def matches_freeling(data):
    dic={'sentences':data}
    response=requests.post(backend_freeling,json=dic)
    parseado=parser(response.text,data)
    return parseado

'''data="Manejo de errores: Actualmente, el código no maneja posibles errores que puedan ocurrir durante el procesamiento del texto. Sería útil agregar algún tipo de manejo de errores para capturar excepciones y devolver mensajes de error apropiados cuando sea necesario."
dic={'sentences':data}
response=requests.post("http://localhost:5002/morfo",json=dic)
parseado=parser(response.text,data)
print(parseado)'''