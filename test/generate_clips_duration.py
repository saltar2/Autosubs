import os
from mutagen.mp3 import MP3
from tqdm import tqdm
import concurrent.futures

def get_audio_files(directory):
    audio_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.wav', '.ogg', '.flac')):  # Agrega más extensiones si es necesario
                audio_files.append(os.path.join(root, file))
    return audio_files

def get_duration(audio_file):
    info = MP3(audio_file)
    duration_ms=info.info.length*1000
    return int(duration_ms)  # Convertir a milisegundos

def save_duration(audio_file):
    duration = get_duration(audio_file)
    file_name = os.path.basename(audio_file)
    return f"{file_name}\t{duration}"

def save_durations_to_tsv(audio_files, output_file):
    with open(output_file, 'w') as f:
        f.write("clip\tduration[ms]\n")
        with concurrent.futures.ProcessPoolExecutor(max_workers=50) as executor:
            results = list(tqdm(executor.map(save_duration, audio_files), total=len(audio_files), desc="Processing", unit="files"))
            for result in results:
                f.write(f"{result}\n")

def generate_clip_info(lan,directory):
    output_file = "clip_durations.tsv"

    audio_files = get_audio_files(os.path.join(directory, lan, "clips"))
    save_durations_to_tsv(audio_files, os.path.join(directory, lan, output_file))

    print(f"Duraciones de los clips guardadas en {output_file}")
