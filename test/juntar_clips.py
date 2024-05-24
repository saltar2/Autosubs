import os
from pydub import AudioSegment
from tqdm import tqdm

def listar_archivos_audio(directorio):
    """Lista los archivos de audio en el directorio especificado."""
    formatos_permitidos = (".mp3", ".wav", ".flac", ".ogg")
    archivos_audio = [f for f in os.listdir(directorio) if f.lower().endswith(formatos_permitidos)]
    archivos_audio.sort()
    return archivos_audio

def unir_audios_con_separacion(directorio, archivos_audio, salida, separacion_s=1.25):
    """Une los archivos de audio con una separación especificada usando Pydub."""
    audio_final = AudioSegment.empty()
    silencio = AudioSegment.silent(duration=separacion_s * 1000)  # Crear segmento de silencio

    # Concatenar archivos con silencios entre ellos
    for archivo in tqdm(archivos_audio, desc="Procesando archivos"):
        ruta_archivo = os.path.join(directorio, archivo)
        audio_segmento = AudioSegment.from_file(ruta_archivo)
        audio_final += audio_segmento + silencio

    # Eliminar el último silencio agregado
    audio_final = audio_final[:-len(silencio)]

    # Guardar el archivo de audio final
    audio_final.export(salida, format="mp3")

def main():
    lan = "en"
    base_dir = r'C:\Users\salva\Downloads\cv-corpus-17.0-delta-2024-03-15'
    directorio = os.path.join(base_dir, lan, 'clips')
    ruta_salida = os.path.join(base_dir, lan, f"salida_{lan}.mp3")

    # Listar y ordenar archivos de audio
    archivos_audio = listar_archivos_audio(directorio)

    # Unir audios con separación usando Pydub
    unir_audios_con_separacion(directorio, archivos_audio, ruta_salida)

    print(f"Audio final guardado en {ruta_salida}")

if __name__ == "__main__":
    main()
