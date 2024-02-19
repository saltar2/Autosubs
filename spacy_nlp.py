import spacy
import srt,configparser
from spacy.tokens import Doc
from spacy.matcher import Matcher
import concurrent.futures,queue, multiprocessing,logging
import openai

# Configura tu clave de API de OpenAI

config=configparser.ConfigParser()
config.read('.env')
openai.api_key=config.get('API_KEYS','CHATGPT_API')

nlp = spacy.load("es_dep_news_trf")
matcher = Matcher(nlp.vocab)

# Lista de reglas gramaticales
grammatical_rules = [
    {"label": "component", "pattern": [{"pos": {"in": ["DET"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADP"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["CONJ"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["PRON"]}, "dep": {"in": ["nsubj", "obj"]}}]},
    {"label": "component", "pattern": [{"pos": {"in": ["VERB"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADV"]}, "dep": "ROOT"}]},
    {"label": "component", "pattern": [{"pos": {"in": ["ADP"]}, "dep": "ROOT"}]},
]

for rule in grammatical_rules:
    matcher.add(rule["label"], [rule["pattern"]])

def split_sentence(sentence):
    doc = nlp(sentence)
    matches = matcher(doc)

    if matches:
        match_id, start, end = matches[0]
        return doc[:end].text, doc[end:].text
    else:
        return sentence, ""

def divide_oraciones(remaining_text, duration, max_chars=40, min_duration=1, margin=8):
    lines = []
    accumulated_line = ""

    while remaining_text:
        line, remaining_text = split_sentence(remaining_text)

        # Verifica si la longitud de la línea supera el límite máximo
        if len(line) > max_chars:
            # Tokeniza la línea en palabras
            words = line.split()

            # Divide la línea en fragmentos sin romper palabras
            fragments = []
            current_fragment = ""

            for word in words:
                if len(current_fragment) + len(word) <= max_chars:
                    current_fragment += ' ' + word
                else:
                    fragments.append(current_fragment.strip())
                    current_fragment = word

            fragments.append(current_fragment.strip())

            for fragment in fragments:
                # Acumula fragmentos hasta alcanzar la duración mínima
                if len(accumulated_line) + len(fragment) <= max_chars + margin and duration + len(accumulated_line.split()) / 3 >= min_duration:
                    accumulated_line += ' ' + fragment
                else:
                    lines.append(accumulated_line.strip())
                    accumulated_line = fragment

        else:
            # Acumula líneas hasta alcanzar la duración mínima
            if len(accumulated_line) + len(line) <= max_chars + margin and duration + len(line.split()) / 3 >= min_duration:
                accumulated_line += ' ' + line
            else:
                lines.append(accumulated_line.strip())
                accumulated_line = line

    if accumulated_line:
        lines.append(accumulated_line.strip())

    return lines

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



def split_sentence_with_gpt(sentence):
    # Llama a la API de ChatGPT para dividir la oración en líneas
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=sentence,
        max_tokens=50,
        temperature=0.5,
        stop=None
    )

    # Obtiene la respuesta generada por la API
    generated_text = response['choices'][0]['text'].strip()

    return generated_text

def divide_oraciones_with_gpt(remaining_text, duration, max_chars=40, min_duration=1, margin=8):
    lines = []
    accumulated_line = ""

    while remaining_text:
        line = split_sentence_with_gpt(remaining_text)

        # Verifica si la longitud de la línea supera el límite máximo
        if len(line) > max_chars:
            # Tokeniza la línea en palabras
            words = line.split()

            # Divide la línea en fragmentos sin romper palabras
            fragments = []
            current_fragment = ""

            for word in words:
                if len(current_fragment) + len(word) <= max_chars:
                    current_fragment += ' ' + word
                else:
                    fragments.append(current_fragment.strip())
                    current_fragment = word

            fragments.append(current_fragment.strip())

            for fragment in fragments:
                # Acumula fragmentos hasta alcanzar la duración mínima
                if len(accumulated_line) + len(fragment) <= max_chars + margin and duration + len(accumulated_line.split()) / 3 >= min_duration:
                    accumulated_line += ' ' + fragment
                else:
                    lines.append(accumulated_line.strip())
                    accumulated_line = fragment

        else:
            # Acumula líneas hasta alcanzar la duración mínima
            if len(accumulated_line) + len(line) <= max_chars + margin and duration + len(line.split()) / 3 >= min_duration:
                accumulated_line += ' ' + line
            else:
                lines.append(accumulated_line.strip())
                accumulated_line = line

    if accumulated_line:
        lines.append(accumulated_line.strip())

    return lines



def dividir_lineas(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as file:
        subtitles = list(srt.parse(file.read()))

    new_subtitles = []

    for subtitle in subtitles:
        text = subtitle.content

        # Aplica el matcher solo si la longitud del subtítulo supera los 40 caracteres
        if len(text) > 40:
            #lines = divide_oraciones(text, subtitle.end.total_seconds() - subtitle.start.total_seconds())
            lines=divide_oraciones_with_gpt(text, subtitle.end.total_seconds() - subtitle.start.total_seconds())
        else:
            lines = [text]

        total_words = sum(len(line.split()) for line in lines)
        original_duration = subtitle.end.total_seconds() - subtitle.start.total_seconds()

        for i, line in enumerate(lines):
            # Evitar que los signos de puntuación aparezcan al principio de una línea
            if i > 0 and line and line[0] in ",.!?":
                new_subtitles[-1].content += line[0]
                line=line[1:]
            
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

    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(srt.compose(new_subtitles))



'''if __name__ == '__main__':
    dividir_lineas("Traducidos\\FLCL Shoegaze - S05E01 - Furu-Bari (Full Barricade).spa.srt",
               "Traducidos\\FLCL Shoegaze - S05E01 - Furu-Bari (Full Barricade).v2.spa.srt")'''