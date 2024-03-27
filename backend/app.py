
import transcription_translation as trtr,extract_audio as extract_audio,time,os,srt
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

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

def principal_v2(video_file,lan):#funcion para web
    video_filename = os.path.join(backend_app.config['TEMP'], secure_filename(video_file.filename))
    video_file.save(video_filename)
    audio_path=extract_audio.extract_audio_ffmpeg(os.path.join(backend_app.config['TEMP']),lan)
    
    sub=trtr.main(audio_path,lan)

    os.remove(audio_path)
    os.remove(video_filename)
    return sub



backend_app = Flask(__name__)
backend_app.config['MAX_CONTENT_LENGTH'] = 2048 * 1024 * 1024#permitimos 2 GB
backend_app.config['TEMP']='temp'
os.makedirs(backend_app.config['TEMP'], exist_ok=True)

@backend_app.route('/language_codes', methods=['GET'])
def get_language_codes():
        return jsonify(language_codes)

@backend_app.route('/process_video', methods=['POST'])
def process_video():
        # Obtiene los datos del formulario enviado por el frontend
    lan = request.form.get('language')
    video_file= request.files['file']
    

        # Llama a la función de procesamiento principal
    subs = principal_v2(video_file, lan)
    
    '''#subtitle example
    import srt,datetime
    
    sub=srt.Subtitle(
                        index=1,
                        start=datetime.timedelta(seconds=2),
                        end=datetime.timedelta(seconds=5),
                        content='Subtitulo de prueba',)'''
    
    result=srt.compose(subs)

        # Devuelve el resultado al frontend
    return jsonify(result)

if __name__ == '__main__':
    backend_app.run(host='0.0.0.0', port=5001)  # Cambia el puerto según tus necesidades
