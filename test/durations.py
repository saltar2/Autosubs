import csv

def get_durations(lan):

    #lan='ru_2'
    # Rutas a los archivos
    validated_file = rf'C:\Users\salva\Downloads\cv-corpus-17.0-delta-2024-03-15\{lan}\validated.tsv'
    clip_duration_file = rf'C:\Users\salva\Downloads\cv-corpus-17.0-delta-2024-03-15\{lan}\clip_durations.tsv'

    # Leer los nombres de los clips desde el archivo validated.tsv
    validated_clips = set()
    with open(validated_file, 'r', encoding='utf-8') as vf:
        reader = csv.DictReader(vf, delimiter='\t')
        for row in reader:
            validated_clips.add(row['path'])

    # Leer las duraciones de los clips desde el archivo clip_duration.tsv
    clip_durations = {}
    with open(clip_duration_file, 'r', encoding='utf-8') as cf:
        reader = csv.DictReader(cf, delimiter='\t')
        for row in reader:
            clip_durations[row['clip']] = int(row['duration[ms]'])

    # Sumar las duraciones de los clips presentes en validated.tsv
    total_duration_ms = 0
    for clip in validated_clips:
        if clip in clip_durations:
            total_duration_ms += clip_durations[clip]

    # Convertir la duración total a un formato legible (opcional)
    total_duration_seconds = total_duration_ms / 1000
    total_duration_minutes = total_duration_seconds / 60
    total_duration_hours = total_duration_minutes / 60
    print(f"Audios for language {lan}")
    print(f"Duración total de los clips en validated.tsv: {total_duration_ms} ms")
    print(f"Duración total de los clips en validated.tsv: {total_duration_seconds:.2f} segundos")
    print(f"Duración total de los clips en validated.tsv: {total_duration_minutes:.2f} minutos")
    print(f"Duración total de los clips en validated.tsv: {total_duration_hours:.2f} horas")
