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
        install_package("spacy")
        download_spacy_model(model)
        models[lang] = spacy.load(model)

def read_srt_files(file_list):
    """Lee los archivos SRT y devuelve el texto concatenado."""
    text = ""
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            subs = srt.parse(f.read())
            for sub in subs:
                text += sub.content + "\n"
    return text

def parse_validate_tsv(file_path):
    """Parses the validate.tsv file para extraer y ordenar path y sentence."""
    df = pd.read_csv(file_path, sep='\t')
    df_filtered = df[['path', 'sentence']]
    df_sorted = df_filtered.sort_values(by='path')
    text = "\n".join(df_sorted['sentence'].tolist())
    return text

def chunk_text(text, max_size=15000):
    """Divide el texto en fragmentos más pequeños que max_size bytes."""
    chunks = []
    current_chunk = ""
    for line in text.split("\n"):
        if len(current_chunk) + len(line) + 1 > max_size:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += "\n" + line if current_chunk else line
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def normalize_text(text):
    """Normaliza el texto eliminando signos de puntuación y convirtiendo a minúsculas."""
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.lower()
    return text

def process_text(text, lang):
    """Procesa el texto con spaCy y lo normaliza."""
    nlp = models[lang]
    doc = nlp(text)
    normalized_text = normalize_text(doc.text)
    lines = normalized_text.split("\n")
    return lines

def save_to_file(lines, output_path):
    """Guarda las líneas en un archivo TXT."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

def convert_srt_to_txt(base_route, lang, output_path):
    """Convierte una lista de archivos SRT en un archivo TXT."""
    transcription_path = os.path.join(base_route, lang)
    srt_files = [os.path.join(transcription_path, f) for f in os.listdir(transcription_path) if f.endswith('.srt')]
    srt_files = sorted(srt_files)

    text = read_srt_files(srt_files)
    text_chunks = chunk_text(text)
    lines = []
    for chunk in text_chunks:
        lines.extend(process_text(chunk, lang))
    save_to_file(lines, output_path)

def convert_tsv_to_txt(base_route, language, output_file):
    text = parse_validate_tsv(os.path.join(base_route, language, 'validated.tsv'))
    text_chunks = chunk_text(text)
    lines = []
    for chunk in text_chunks:
        lines.extend(process_text(chunk, language))
    save_to_file(lines, output_file)

# Ruta base y idioma correspondiente
base_route = "test\\langs"
language = 'ja'  # Cambia esto al idioma correspondiente: 'en', 'it', 'ru' o 'ja'

# Ruta de salida para el archivo TXT
output_file = f'output_{language}.txt'
input_file = f'input_{language}.txt'  # archivo de salida para transcripciones source

# Convierte los archivos SRT en un archivo TXT
convert_srt_to_txt(base_route, language, os.path.join(base_route, language, output_file))
convert_tsv_to_txt(base_route, language, os.path.join(base_route, language, input_file))
print(f"Archivo TXT guardado en {output_file}")
print(f"Archivo TXT guardado en {input_file}")
