
import transcription_translation as trtr,extract_audio as extract_audio,time,os
from flask import Flask, request, jsonify

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

def principal(current_directory,lan):#funcion para local sin web
    extract_audio.extract_audio_ffmpeg(current_directory,lan)

    audio_files = [f for f in os.listdir(current_directory) if f.lower().endswith(('.wav'))]#vamos a procesar una lista de audios si fuese necesario

    for aud in audio_files:
        trtr.main(os.path.join(current_directory,aud),lan)
        os.remove(os.path.join(current_directory,aud))

def principal_v2(video_file,lan):#funcion para web

    audio=extract_audio.extract_audio_ffmpeg_v2(video_file,lan)
    
    sub=trtr.main_v2(audio,lan)

    os.remove(audio)
    return sub


web=True
if web:
    app = Flask(__name__)

    @app.route('/language_codes', methods=['GET'])
    def get_language_codes():
        return jsonify(language_codes)

    @app.route('/process_video', methods=['POST'])
    def process_video():
        # Obtiene los datos del formulario enviado por el frontend
        lan = request.form.get('language')
        video_file = request.files['file']

        # Llama a la función de procesamiento principal
        #result = principal_v2(video_file, lan)

        #subtitle example
        import srt,datetime
        subs=[]
        sub=srt.Subtitle(
                        index=1,
                        start=datetime.timedelta(seconds=2),
                        end=datetime.timedelta(seconds=5),
                        content='Subtitulo de prueba',)
        subs.append(sub)
        result=srt.compose(subs)

        # Devuelve el resultado al frontend
        return jsonify(result)

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5001)  # Cambia el puerto según tus necesidades
else:
    #lan='japanese'
    lan='english'
    #current_directory="E:\Autosubs\TFG_compartido"#para escritorioy

    current_directory=os.path.join(os.getcwd(), "TFG_compartido")
    download_dir=""
    upload_dir=""

    start_time=time.time()

    principal(current_directory,lan)

    end_time=time.time()
    print("Tiempo total : "+str((end_time-start_time)/60)+" minutos")