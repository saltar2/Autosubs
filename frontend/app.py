from flask import Flask, render_template, request, redirect, url_for, send_file,jsonify,abort,Response
import os, requests,time,threading,datetime
from multiprocessing import Queue
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import zipfile


# Configuración de la aplicación
app = Flask(__name__)

#docker url
url_base='http://backend:5001'
#local url
#url_base='http://localhost:5001'
# Configuración de la subida de archivos

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'm4v', 'mts', 'wmv', 'mpg', 'flv','mp3','flac','aac'}

app.config['MAX_CONTENT_LENGTH'] = 2048 * 1024 * 1024  # Permitimos hasta 2 GB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

processing_progress=0
num_files=0
num_ses_messages=6
language_codes={}
sse_connection_with_backend=None
event_queue = Queue()

# Función para verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/progress',methods=['GET'])
def prog_var():
    global processing_progress
    max_long=num_files*num_ses_messages
    progress=round((processing_progress/max_long)*100,1)
    return jsonify({'progress': progress})

@app.route('/language_codes',methods=['GET'])
def codes():
    try:
        global language_codes
        backend_url = url_base + '/language_codes'
        response = requests.get(backend_url)
        response.raise_for_status()  # Lanzar una excepción si la solicitud falla
        language_codes = response.json()
        return language_codes,200
    except requests.exceptions.RequestException:
        # Manejar la excepción en caso de que la solicitud falle
        #print(f"Error al obtener los códigos de idioma: {e}")
        return language_codes,500
# Ruta para la página de inicio
@app.route('/')
def index():
    global language_codes
    return render_template('index.html', language_codes=language_codes)

@app.route('/upload', methods=['POST'])
def upload_files():
    start=time.time()
    uploaded_files = request.files.getlist('file')
    lan = request.form.get('language')
    augmented_by_llm=False
        # Guardar archivos y obtener los subtítulos procesados
    subs,text_correction = process_files(uploaded_files, lan,augmented_by_llm)

        # Generar archivo ZIP con los subtítulos
    zip_filename = generate_zip(uploaded_files, subs ,text_correction)
 
        # Generar la URL de descarga
    zip_url = url_for('download_zip', filename=zip_filename)
    end=time.time()
    tot=(end-start)/60
    print(f"Tiempo total: {str(tot)}")
        # Retornar la URL de descarga
    return zip_url

def process_files(uploaded_files, lan,augmented_by_llm:bool):
    subs = []
    texts = []
    
    global processing_progress
    processing_progress=0
    global num_files
    num_files=len(uploaded_files)
    #long=len(uploaded_files)*num_ses_messages
    #cont=0
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            try:
            # Enviar archivo al backend y obtener subtítulo
                res = send_to_backend(filepath, filename, lan,file.mimetype,augmented_by_llm)
                subtitle=res['subs']
                text_correction=res['text_correction']
            finally:
                os.remove(filepath)
            subs.append(subtitle)
            texts.append(text_correction)
            #cont+=1
            #processing_progress=round((cont/long)*100,1)
    return subs,texts

def send_to_backend(filepath, filename, lan, mimetype,augmented_by_llm:bool):
    backend_url = url_base + '/process_video'
    files = {'file': (filename, open(filepath, 'rb').read(), mimetype)}
    data = {'language': lan,'augmented llm':augmented_by_llm}
    
    try:
        response = requests.post(backend_url, data=data, files=files)
        if not response.ok:
            error_menssage=response.text    
        response.raise_for_status()  # Lanza una excepción si el código de estado de la respuesta no es 2xx
        
        return response.json()
    except requests.exceptions.RequestException as e:
        # Error de conexión , tiempo de espera, problemas con apis etc
        abort(503,error_menssage)
    except Exception as e :
        abort(500,error_menssage)

def generate_zip(uploaded_files, subs,text_corrected):
    zip_filename = 'subtitles.zip'
    extension = ".es.srt"
    extension2= ".txt"
    with zipfile.ZipFile(os.path.join(app.config['DOWNLOAD_FOLDER'], zip_filename), 'w') as zipf:
        for i, subtitle in enumerate(subs, start=1):
            video_name = os.path.splitext(uploaded_files[i - 1].filename)[0]
            subtitle_filename = f'{video_name}{extension}'
            text_filename= f'{video_name}{extension2}'
            zipf.writestr(subtitle_filename, subtitle)
            zipf.writestr(text_filename,text_corrected[i-1])
    return zip_filename

                               
@app.route('/download/<filename>')
def download_zip(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)

'''@app.route('/event')
def sse_endpoint():
    backend_response = requests.get(url_base+'/event', stream=True)
    #global processing_progress,num_files
    #max_long=num_files*num_ses_messages
    #cont=processing_progress+1
    #processing_progress=round((cont/max_long)*100,1)
    return Response(backend_response.iter_content(), content_type='text/event-stream')'''
@app.route('/event')
def sse_endpoint():
    global sse_connection_with_backend
    if sse_connection_with_backend is None:
        get_sse_endpoint_backend()
    event_queue.put('start')
    def generate_event():
        while True:
            event=event_queue.get()
            yield "event:message\ndata: {}\n\n".format(event)  
    return Response(generate_event(), content_type='text/event-stream')

def get_sse_endpoint_backend():
    backend_response = requests.get(url_base+'/event', stream=True)
    global sse_connection_with_backend
    sse_connection_with_backend=backend_response.iter_lines()

    def process_backend_response():
        for event in sse_connection_with_backend:
            global processing_progress
            data=event.decode('utf-8')
            if(data != '' and not data.__contains__('start')):
                processing_progress+=1
                print(data)
                event_queue.put(str(data))
             
    print("SSE with backend connected")
    
    threading.Thread(target=process_backend_response).start()
    


@app.errorhandler(500)
def handle_general_error(e):
    if isinstance(e,requests.exceptions.ChunkedEncodingError):
        global sse_connection_with_backend
        sse_connection_with_backend=None
    else:
        return f"An unexpected error occurred: {str(e)}", 500

@app.errorhandler(503)
def handle_specific_error(e):
    return e.description, 503

@app.errorhandler(requests.exceptions.ChunkedEncodingError)
def handle_brute_desconection_with_backend():
    global sse_connection_with_backend
    sse_connection_with_backend=None

@app.route('/healthcheck')
def healthcheck():
    return 'OK', 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,threaded=True,debug=False)
    
    

