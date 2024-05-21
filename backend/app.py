
import transcription_translation as trtr,extract_audio as extract_audio,os,srt,time,exceptions,logging
from multiprocessing import Queue
from flask import Flask, request, jsonify,Response,abort
from werkzeug.utils import secure_filename

event_queue = Queue()

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


def principal(video_file,lan,augmented_by_llm:bool):#funcion para web
   
    video_filename = os.path.join(backend_app.config['TEMP'], secure_filename(video_file.filename))
    video_file.save(video_filename)
    time.sleep(2)
    event_queue.put('Procesando video: {}'.format(video_file.filename))
    try:
        if video_filename.__contains__("aac", "mp3", "flac"): #es un audio
            audio_path=extract_audio.convert_audio_to_wav(os.path.join(backend_app.config['TEMP']))
        else:#es un video
            audio_path=extract_audio.extract_audio_ffmpeg(os.path.join(backend_app.config['TEMP']),lan)
        
        sub,text_correction=trtr.main(audio_path,lan,event_queue,augmented_by_llm)
        
    except exceptions.CustomError:
         raise 
    except Exception:
         raise 

    os.remove(audio_path)
    os.remove(video_filename)
    return sub,text_correction

backend_app = Flask(__name__)
backend_app.config['MAX_CONTENT_LENGTH'] = 2048 * 1024 * 1024#permitimos 2 GB
backend_app.config['TEMP']='temp'
os.makedirs(backend_app.config['TEMP'], exist_ok=True)

file_handler = logging.FileHandler('error.log')
file_handler.setLevel(logging.ERROR)  # Log only ERROR level messages
backend_app.logger.addHandler(file_handler)

@backend_app.route('/language_codes', methods=['GET'])
def get_language_codes():
        return jsonify(language_codes)

@backend_app.route('/process_video', methods=['POST'])
def process_video():
        # Obtiene los datos del formulario enviado por el frontend
    lan = request.form.get('language')
    augmented_by_llm=True if "true" == request.form.get('augmented llm').lower() else False #llega como string aunque lo he mandado como bool
    video_file= request.files['file']
    
    
    try :
        subs,text_correction=principal(video_file, lan,augmented_by_llm)
    except exceptions.CustomError as e:
         abort(503,e)#service unavailable
    except Exception as e:
         abort(500,e)#unexpected error

    result=srt.compose(subs)
    response_data = {
        'subs': result,
        'text_correction': text_correction
    }
    # Devuelve el resultado al frontend
    return jsonify(response_data)


@backend_app.route('/event')
def sse_endpoint():
    event_queue.put('start')
    def generate_event():
        while True:
            event=event_queue.get()
            formated_event= f"{event}\n\n"
            yield formated_event
            print(event)
    
    return Response(generate_event(), content_type='text/event-stream')

@backend_app.errorhandler(500)
def handle_general_error(e):
    backend_app.logger.error(e)
    return str(e.description),500

@backend_app.errorhandler(503)
def handle_specific_error(e):
    backend_app.logger.error(e)
    return str(e.description),503

@backend_app.route('/healthcheck')
def healthcheck():
    return 'OK', 200

if __name__ == '__main__':
    backend_app.run(host='0.0.0.0', port=5001,threaded=True,debug =False)  # Cambia el puerto según tus necesidades
    
    

