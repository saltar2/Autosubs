
import transcription_translation as trtr,extract_audio,time,os
language_codes = {
    #"chinese": ["zh"],
    "czech" : ["cs"],
    "danish": ["da"],
    "dutch": ["nl"],
    "english": ["en"],
    "french": ["fr"],
    "german": ["de"],
    "greek" : ["el"],
    "hindi": ["hi"],
    "indonesian": ["id"],
    "italian": ["it"],
    "japanese": ["ja"],
    "korean": ["ko"],
    "norwegian": ["no"],
    "polish": ["pl"],
    "portuguese": ["pt"],
    "russian": ["ru"],
    "spanish": ["es"],
    "swedish": ["sv"],
    "turkish": ["tr"],
    "ukrainian": ["uk"]
}
#lan='japanese'
lan='english'
#current_directory="E:\Autosubs\TFG_compartido"#para escritorioy

current_directory=os.path.join(os.getcwd(), "TFG_compartido")

start_time=time.time()
extract_audio.extract_audio_ffmpeg_v2(current_directory,lan)

audio_files = [f for f in os.listdir(current_directory) if f.lower().endswith(('.wav'))]#vamos a procesar una lista de audios si fuese necesario

for aud in audio_files:
    trtr.main(os.path.join(current_directory,aud),lan)
    os.remove(os.path.join(current_directory,aud))

end_time=time.time()
print("Tiempo total : "+str((end_time-start_time)/60)+" minutos") 