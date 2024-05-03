
import transcription_translation as trtr,extract_audio as extract_audio,os,srt,time,exceptions
from multiprocessing import Queue
from flask import Flask, request, jsonify,Response
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

'''def principal_v2(video_file,lan,queue):#funcion para web
    time.sleep(1)
    event_queue.put('Procesando video: {}'.format(video_file.filename))
    
    video_filename = os.path.join(backend_app.config['TEMP'], secure_filename(video_file.filename))
    video_file.save(video_filename)
    event_queue.put('Extrayendo audio ...')
    time.sleep(1)
    audio_path=extract_audio.extract_audio_ffmpeg(os.path.join(backend_app.config['TEMP']),lan)
    
    sub=trtr.main(audio_path,lan,event_queue)

    os.remove(audio_path)
    os.remove(video_filename)
    queue.put(sub)'''

def principal(video_file,lan):#funcion para web
   
    video_filename = os.path.join(backend_app.config['TEMP'], secure_filename(video_file.filename))
    video_file.save(video_filename)
    event_queue.put('Procesando video: {}'.format(video_file.filename))
    try:
        audio_path=extract_audio.extract_audio_ffmpeg(os.path.join(backend_app.config['TEMP']),lan)
        
        sub=trtr.main(audio_path,lan,event_queue)
    except exceptions.CustomError as a:
         raise 
    except Exception as e:
         raise 

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
    
    try :
        subs=principal(video_file, lan)
    except exceptions.CustomError as e:
         return jsonify(error=str(e)),503#service unavailable
    except Exception as e:
         return jsonify(error=str(e)),500#unexpected error
    ###
    '''subs=[]
    #subtitle example
    import srt,datetime
    
    sub=srt.Subtitle(
                        index=1,
                        start=datetime.timedelta(seconds=2),
                        end=datetime.timedelta(seconds=5),
                        content='Subtitulo de prueba',)
    subs.append(sub)
    time.sleep(5)'''
    ###
    result=srt.compose(subs)

    # Devuelve el resultado al frontend
    return jsonify(result)


@backend_app.route('/event')
def sse_endpoint():
    def generate_event():
        while True:
            event=event_queue.get()
            yield "data: {}\n\n".format(event)
            #print(event)
            #time.sleep(0.6)     
    return Response(generate_event(), content_type='text/event-stream')
@backend_app.route('/healthcheck')
def healthcheck():
    return 'OK', 200
if __name__ == '__main__':
    backend_app.run(host='0.0.0.0', port=5001,threaded=True,debug =False)  # Cambia el puerto según tus necesidades
    
    
'''lan="japanese"
audio_path=extract_audio.extract_audio_ffmpeg("/home/salva/Autosubs/backend/temp",lan)
    
sub=trtr.main(audio_path,lan,event_queue)
result=srt.compose(sub)
name='temp/'+os.path.splitext(os.path.basename(audio_path))[0]+".srt"
with open(name, "a", encoding='utf-8') as a:
    a.write(result)

os.remove(audio_path)'''
