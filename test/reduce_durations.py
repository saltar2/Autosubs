import csv,os

base_dir="test\langs"
lan="es"

# Definir el archivo de entrada y salida
input_file = os.path.join(base_dir,lan,'clip_durations.tsv')
output_file = os.path.join(base_dir,lan,'clip_durations_reduced.tsv')
validate_file = os.path.join(base_dir, lan, 'validated.tsv')
validate_reduced_file = os.path.join(base_dir, lan, 'validated_reduced.tsv')
# Leer el archivo de entrada
with open(input_file, 'r', newline='',encoding='utf-8') as infile:
    reader = csv.DictReader(infile, delimiter='\t')
    clips = list(reader)

# Sumar las duraciones y seleccionar los clips
total_duration = 0
selected_clips = []
max_duration = 120 * 60 * 1000  # 120 minutos en milisegundos

for clip in clips:
    duration = int(clip['duration[ms]'])
    if total_duration + duration > max_duration:
        break
    selected_clips.append(clip)
    total_duration += duration

# Escribir el archivo de salida
with open(output_file, 'w', newline='',encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=['clip', 'duration[ms]'], delimiter='\t')
    writer.writeheader()
    writer.writerows(selected_clips)

print(f"Archivo {output_file} generado con éxito.")

# Obtener los clips seleccionados para hacer el join
selected_clip_names = {clip['clip'] for clip in selected_clips}

# Leer el archivo validate.tsv y hacer el join
with open(validate_file, 'r', newline='', encoding='utf-8') as validate_infile:
    validate_reader = csv.DictReader(validate_infile, delimiter='\t')
    
    # Verifica si cada path tiene la extensión .mp3, si no la tiene, se la añade
    validate_rows = []
    for row in validate_reader:
        path = row['path']
        if not path.endswith('.mp3'):
            path += '.mp3'
        if path in selected_clip_names:
            row['path'] = path
            validate_rows.append(row)

# Escribir el archivo validate_reduced.tsv
with open(validate_reduced_file, 'w', newline='',encoding='utf-8') as validate_outfile:
    fieldnames = validate_reader.fieldnames  # Usar los mismos encabezados del archivo validate.tsv
    validate_writer = csv.DictWriter(validate_outfile, fieldnames=fieldnames, delimiter='\t')
    validate_writer.writeheader()
    validate_writer.writerows(validate_rows)

print(f"Archivo {validate_reduced_file} generado con éxito.")
