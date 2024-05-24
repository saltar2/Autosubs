import srt
import subprocess
import sys
import spacy
import os
import string
import pandas as pd


# Función para instalar un paquete con subprocess
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# Función para descargar un modelo de spaCy
def download_spacy_model(model):
    subprocess.check_call([sys.executable, "-m", "spacy", "download", model])


models_to_install = {
    "en": "en_core_web_sm",
    "it": "it_core_news_sm",
    "ru": "ru_core_news_sm",
    "ja": "ja_core_news_sm"
}

# Intenta cargar los modelos, y si falla, los instala y los carga de nuevo
models = {}
for lang, model in models_to_install.items():
    try:
        models[lang] = spacy.load(model)
    except OSError:
        print(f"Modelo {model} no encontrado. Instalando...")
        install_package(f"spacy")
        download_spacy_model(model)
        models[lang] = spacy.load(model)


def read_srt_files(file_list):
    """Lee los archivos SRT y devuelve el texto concatenado."""
    text = ""
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            subs = srt.parse(f.read())
            for sub in subs:
                text += sub.content + " "
    return text


def parse_validate_tsv(file_path):
    """Parses the validate.tsv file to extract and order path and sentence."""
    # Leer el archivo TSV
    df = pd.read_csv(file_path, sep='\t')

    # Filtrar las columnas necesarias
    df_filtered = df[['path', 'sentence']]

    # Ordenar los datos por 'path'
    df_sorted = df_filtered.sort_values(by='path')
    text = " ".join(df_sorted['sentence'].tolist())
    return text


def chunk_text(text, max_size=15000):
    """Divide el texto en fragmentos más pequeños que max_size bytes."""
    chunks = []
    current_chunk = ""
    for word in text.split():
        if len(current_chunk) + len(word) + 1 > max_size:
            chunks.append(current_chunk)
            current_chunk = word
        else:
            current_chunk += " " + word if current_chunk else word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def process_text(text, lang):
    """Procesa el texto con spaCy y extrae los detalles necesarios."""
    nlp = models[lang]  # Selecciona el modelo spaCy según el idioma
    doc = nlp(text)
    data = []
    for token in doc:
        if token.text in string.punctuation:
            continue  # Ignora los signos de puntuación
        data.append({
            "token": token.text,
            "speaker": 0,
            "ts": "",  # timestamp no disponible en procesamiento solo de texto
            "endTs": "",  # end timestamp no disponible en procesamiento solo de texto
            "punctuation": token.whitespace_,
            "case": "UC" if token.is_upper else ("LC" if token.is_lower else "CA"),
            "tags": [],
            "wer_tags": []
        })
    return data


def save_to_file(data, output_path):
    """Guarda los datos en un archivo NLP."""
    df = pd.DataFrame(data)
    df.to_csv(output_path, sep="|", index=False)


def convert_srt_to_nlp(base_route, lang, output_path):
    """Convierte una lista de archivos SRT en un archivo NLP."""
    transcription_path = os.path.join(base_route, language, f"subtitles_{lang}")
    srt_files = [os.path.join(transcription_path, f) for f in os.listdir(transcription_path) if f.endswith('.srt')]
    srt_files = sorted(srt_files)  # ordenamos

    text = read_srt_files(srt_files)
    text_chunks = chunk_text(text)
    data = []
    for chunk in text_chunks:
        data.extend(process_text(chunk, lang))
    save_to_file(data, output_path)


def convert_tsv_to_nlp(base_route, language, output_file):
    text = parse_validate_tsv(os.path.join(base_route, language, 'validated.tsv'))
    text_chunks = chunk_text(text)
    data = []
    for chunk in text_chunks:
        data.extend(process_text(chunk, language))
    save_to_file(data, output_file)


# Ruta base y idioma correspondiente
base_route = "C:\\Users\\salva\\Downloads\\cv-corpus-17.0-delta-2024-03-15"
language = 'en'  # Cambia esto al idioma correspondiente: 'en', 'it', 'ru' o 'ja'

# Ruta de salida para el archivo NLP
output_file = f'output_{language}.nlp'
input_file = f'input_{language}.nlp'  # archivo de salida para transcripciones source

# Convierte los archivos SRT en un archivo NLP
convert_srt_to_nlp(base_route, language, os.path.join(base_route, language, output_file))
convert_tsv_to_nlp(base_route, language, os.path.join(base_route, language, input_file))
print(f"Archivo NLP guardado en {output_file}")
print(f"Archivo NLP guardado en {input_file}")


'''
docker run -v E:\FSTAlign\speech-datasets\earnings21\output\:/fstalign/outputs -v E:\FSTAlign\speech-datasets\earnings21\transcripts\:/fstalign/references --name fstaling -it revdotcom/fstalign

./build/fstalign wer --ref references/mi/en/input_en.nlp --hyp outputs/mi/en/output_en.nlp
'''