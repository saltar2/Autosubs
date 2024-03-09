
import srt,languagecodes,unicodedata,configparser,deepl
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

    for i, l in enumerate(lines):
        if i % 30 == 0:
            # Split lines into smaller groups, to prevent error 413
            grouped_lines.append([])
            if i != 0:
                # Include previous 3 lines, to preserve context between splits
                grouped_lines[-1].extend(grouped_lines[-2][-3:])
        grouped_lines[-1].append(l.strip())
            
    try:
        translator = deepl.Translator(deepl_authkey)
        for i, n in enumerate(tqdm(grouped_lines)):
            x = ["\n".join(n).strip()]
            if language.lower() == "japanese":
                result = translator.translate_text(x, source_lang="JA", target_lang=deepl_target_lang)
            else:#default language
                result = translator.translate_text(x,source_lang='EN', target_lang=deepl_target_lang)
            english_tl = result[0].text.strip().splitlines()
            assert len(english_tl) == len(n), ("Invalid translation line count ("+ str(len(english_tl))+ " vs "+ str(len(n))+ ")")
            if i != 0:
                english_tl = english_tl[3:]
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


