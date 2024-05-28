import os
import csv
def delete_not_validated(base_dir):
    # Ruta al directorio donde se encuentran validated.tsv y la carpeta clips
    #base_dir = r'C:\Users\salva\Downloads\cv-corpus-17.0-delta-2024-03-15\ru_2'

    # Cambiar el directorio actual
    #os.chdir(base_dir)
    # Ruta al archivo validated.tsv
    tsv_file = os.path.join(base_dir,'validated.tsv')
    #tsv_file = os.path.join(base_dir,'clip_durations_reduced.tsv')
    # Ruta a la carpeta clips
    clips_folder = os.path.join(base_dir,'clips')

    # Leer los nombres de los archivos de audio desde el archivo validated.tsv
    audio_files_in_tsv = set()

    with open(tsv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            audio=row['path']
            #audio=row['clip']
            if not audio.__contains__('.mp3'):
                audio=audio+".mp3"
            audio_files_in_tsv.add(audio)
            
    a=len(audio_files_in_tsv)

    # Obtener los nombres de los archivos en la carpeta clips
    audio_files_in_clips = set(os.listdir(clips_folder))
    b=len(audio_files_in_clips)
    # Identificar los archivos en la carpeta clips que no están en el archivo validated.tsv
    files_to_remove = audio_files_in_clips - audio_files_in_tsv
    c=len(files_to_remove)
    # Eliminar los archivos no deseados
    for file in files_to_remove:
        file_path = os.path.join(clips_folder, file)
        os.remove(file_path)
        #print(f'Removido: {file_path}')

    print('Proceso completado.')
