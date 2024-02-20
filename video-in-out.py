
import transcription_translation as trtr,extract_audio,time,os

#lan='japanese'
lan='english'
#current_directory="C:\\Users\\salva\\Autosubs\\Pruebas"#para escritorio
current_directory="/app/Pruebas"#para docker

start_time=time.time()
extract_audio.extract_audio_ffmpeg_v2(current_directory,lan)

audio_files = [f for f in os.listdir(current_directory) if f.lower().endswith(('.wav'))]#vamos a procesar una lista de audios si fuese necesario

for aud in audio_files:
    trtr.main(os.path.join(current_directory,aud),lan)


end_time=time.time()
print("Tiempo total : "+str((end_time-start_time)/60))