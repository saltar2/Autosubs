
import srt,languagecodes,unicodedata,configparser,deepl,json
from lingua import LanguageDetectorBuilder
from tqdm import tqdm

config=configparser.ConfigParser()
config.read('.env')
deepl_authkey=config.get('API_KEYS','DEEPL_KEY')

# DeepL translation
def deepl_tr(subs,out_path,language,deepl_target_lang,model_size): 
    print("Translating...")
    
    lines = []
    punct_match = ["。", "、", ",", ".", "〜", "！", "!", "？", "?", "-"]
    for i in range(len(subs)):#añadimos distinta puntuacion si es japones o no
        if language.lower() == "japanese":
            if subs[i].content[-1] not in punct_match:
                subs[i].content += "。"
            subs[i].content = "「" + subs[i].content + "」"
        else:
            if subs[i].content[-1] not in punct_match:
                subs[i].content += "."
            subs[i].content = '"' + subs[i].content + '"'

    for i in range(len(subs)):
        lines.append(subs[i].content)

    grouped_lines = []
    english_lines = []
    
  

    detector=LanguageDetectorBuilder.from_all_spoken_languages().build()
    example_lines=detector.detect_languages_in_parallel_of(lines)
    def_language=language

    ant=None
    next=None
    larg=len(example_lines)

    for i in range(larg):#consideramos 2 lineas consecutivas detectan el mismo idioma pertenecen al mismo grupo de idioma

        if(example_lines[i] is not None):
            current=example_lines[i].name.lower()
        else:#caso None normalmente es un numero
            current=def_language

        if(i+1<larg):#todos los casos
            if(example_lines[i+1] is not None):
                next=example_lines[i+1].name.lower()
            else:
                next=def_language

            if(i==0):
                ant=def_language
            else:
                ant=example_lines[i-1]

            if( current!=next and current!=ant):
                example_lines[i]=def_language
                continue
            else:
                example_lines[i]=current

            example_lines[i]=current
            continue       
        
        if(i==larg-1):#ultimo caso
            ant=example_lines[i-1]
            if(current!=ant):# con suficientes caracteres podemos suponer que la deteccion esta bien 
                example_lines[i]=def_language
                continue
            example_lines[i]=current

        
    current_group = []
    fin=len(lines)
    cont=0
    for i, l in enumerate(lines):
        lang = example_lines[i]
        if cont>= 30 :
            grouped_lines.append(current_group)
            current_group=[]
            current_group.append(l)
            cont=1
        else:
            current_group.append(l)
            if(i < fin-1 and lang !=example_lines[i+1]):
                grouped_lines.append(current_group)
                cont=0
                current_group=[]
            elif(i==fin-1):
                grouped_lines.append(current_group)
            else:
                cont+=1
          
    '''for i, l in enumerate(lines):
        if i % 30 == 0:
            # Split lines into smaller groups, to prevent error 413
            grouped_lines.append([])
            if i != 0:
                # Include previous 3 lines, to preserve context between splits
                grouped_lines[-1].extend(grouped_lines[-2][-3:])
        grouped_lines[-1].append(l.strip())'''
    
            
    try:
        translator = deepl.Translator(deepl_authkey)
        for i, n in enumerate(tqdm(grouped_lines)):
            x = ["\n".join(n).strip()] #multiples lineas
            #x=n
            if language.lower() == "japanese":
                result = translator.translate_text(x, source_lang="JA", target_lang=deepl_target_lang)
            else:#default language
                #result = translator.translate_text(x,source_lang='EN', target_lang=deepl_target_lang)
                result = translator.translate_text(x, target_lang=deepl_target_lang)
            english_tl = result[0].text.strip().splitlines()
            assert len(english_tl) == len(n), ("Invalid translation line count ("+ str(len(english_tl))+ " vs "+ str(len(n))+ ")")
            #if i != 0:#quitado para que no agrupe y traduzca linea a linea
                #english_tl = english_tl[3:]
            remove_quotes = dict.fromkeys(map(ord, '"„“‟”＂「」'), None)
            for e in english_tl:
                    english_lines.append(e.strip().translate(remove_quotes).replace("’", "'"))
        for i, e in enumerate(english_lines):
            subs[i].content = e
    except Exception as e:
        print("DeepL translation error:", e)

    #----------------------------------------------------------------------------------
    lan=translate_language_name(deepl_target_lang)
    var=out_path.split(".srt")
    #out_path=var[0]+"."+lan+".srt"
    out_path=var[0]+"."+lan+model_size+".srt"
    with open(out_path, "w", encoding="utf8") as f:
        f.write(srt.compose(subs))
    print("\nDone! Subs written to", out_path)
    return out_path
    

def translate_language_name(language_name):
    """
    Traduce el nombre de una lengua a su ISO 639-2/B.

    Args:
        language_name: El nombre de la lengua a traducir.

    Returns:
        El código ISO 639-2/B de la lengua.
    """
    language_name = language_name.lower()
    language_name = unicodedata.normalize("NFD", language_name)
    language_name = language_name.replace("á", "a")
    language_name = language_name.replace("é", "e")
    language_name = language_name.replace("í", "i")
    language_name = language_name.replace("ó", "o")
    language_name = language_name.replace("ú", "u")

    try:#https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes#es
        iso_code = languagecodes.iso_639_alpha3(language_name)
        return iso_code
    except ValueError:
        print(f"No se encontró el código ISO 639-2/B para el idioma: {language_name}")
        return None

'''def main():
    sorted_results=[]
    with open("deepgram_transcription_nova-2.json", "r", encoding="utf-8") as file:
        sorted_results = json.load(file)
    import datetime
    subs=[]
    out_path='TFG_compartido\\Avalanches_ Unpredictable, Inevitable, Fatal _ Deadly Disasters _ Free Documentary (192kbit_AAC).srt'
    language='english'
    target_lang='ES'
    model_size=".deepgram_nova-2"
    sub_index=1
    for key,value in sorted_results.items():
        for value2 in value["results"]:
            j=0
            subs.append(srt.Subtitle(
                        index=sub_index,
                        start=datetime.timedelta(seconds=sub_index),
                        end=datetime.timedelta(seconds=sub_index+1),
                        content=value2["transcript"].strip(),))
                
            sub_index += 1
    deepl_tr(subs,out_path,language,target_lang,model_size,sorted_results)


main()'''