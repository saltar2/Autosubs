from flask import Flask, render_template, request, redirect, url_for, send_file,jsonify,abort,Response
#from quart import Quart, render_template, request, redirect, url_for, send_file,jsonify,abort,Response
import os, requests,time,threading,datetime
from multiprocessing import Queue
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import zipfile


# Configuración de la aplicación
app = Flask(__name__)
#app = Quart(__name__)

#docker url
url_base='http://backend:5001'
#local url
#url_base='http://localhost:5001'
# Configuración de la subida de archivos

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'm4v', 'mts', 'wmv', 'mpg', 'flv', 'mp3', 'flac', 'aac'}

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 * 2  # Permitimos hasta 2 GB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

processing_progress=0
num_files=0
num_ses_messages=3
language_codes={}
sse_connection_with_backend=None
event_queue = Queue()

batch_results = {'names': [],'subs': [], 'text_correction': []}

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
    #time.sleep(60)
    start=time.time()
    #print(request.files)
    uploaded_files = request.files.getlist('file')
    '''fin_uploaded=time.time()
    uploaded_time=(fin_uploaded-start)/60
    print(uploaded_time)'''
    lan = request.form.get('language')
    augmented_by_llm=True if request.form.get('llm_option') == 'yes' else False

    batch_number = int(request.form.get('batch_number'))
    total_batches = int(request.form.get('total_batches'))
    #filenames_upl=[]
    '''for file in uploaded_files:
        filenames_upl.append(file.filename)'''
    filenames_upl=[file.filename for file in uploaded_files]
    batch_results['names'].extend(filenames_upl)
        # Guardar archivos y obtener los subtítulos procesados
    subs,text_correction = process_files(uploaded_files, lan,augmented_by_llm)

    batch_results['subs'].extend(subs)
    batch_results['text_correction'].extend(text_correction)

    if batch_number == total_batches:
        combined_zip_filename = generate_zip(batch_results['names'],batch_results['subs'], batch_results['text_correction'])
        combined_zip_url = url_for('download_zip', filename=os.path.basename(combined_zip_filename))

        # Limpiar resultados acumulados
        batch_results['subs'].clear()
        batch_results['text_correction'].clear()
        batch_results['names'].clear()
        end=time.time()
        tot=(end-start)/60
        print(f"Tiempo total: {str(tot)}")
        return jsonify({"zip_url": combined_zip_url, "total_time": tot})
    else:
        return jsonify({"zip_url": None, "total_time": None, "batch_number": batch_number})
'''

        # Generar archivo ZIP con los subtítulos
    zip_filename = generate_zip(uploaded_files, subs ,text_correction)
 
        # Generar la URL de descarga
    zip_url = url_for('download_zip', filename=zip_filename)
    end=time.time()
    tot=(end-start)/60
    print(f"Tiempo total: {str(tot)}")
        # Retornar la URL de descarga
    return jsonify({"zip_url":zip_url,"total_time":tot})'''


def process_files(uploaded_files, lan, augmented_by_llm: bool):
    subs = []
    texts = []
    
    global processing_progress
    processing_progress = 0
    global num_files
    num_files = len(uploaded_files)
    
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            try:
                # Enviar archivo al backend y obtener subtítulo
                res = send_to_backend(file, lan, augmented_by_llm)
                subtitle = res['subs']
                text_correction = res['text_correction']
                
                subs.append(subtitle)
                texts.append(text_correction)
            except Exception as e:
                print(f"Error al procesar el archivo: {str(e)}")
                subs.append(None)
                texts.append(None)

    return subs, texts

def send_to_backend(file, lan, augmented_by_llm: bool):
    backend_url = url_base + '/process_video'
    files = {'file': (file.filename, file.stream, file.mimetype)}
    data = {'language': lan, 'augmented llm': augmented_by_llm}
    
    try:
        response = requests.post(backend_url, data=data, files=files)
        response.raise_for_status()  # Lanza una excepción si el código de estado de la respuesta no es 2xx
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Error al enviar el archivo al backend: {str(e)}")
    
def generate_zip(uploaded_files, subs,text_corrected):
    zip_filename = 'subtitles.zip'
    extension = ".es.srt"
    extension2= ".txt"
    with zipfile.ZipFile(os.path.join(app.config['DOWNLOAD_FOLDER'], zip_filename), 'w') as zipf:
        for i, subtitle in enumerate(subs, start=1):
            video_name = os.path.splitext(uploaded_files[i - 1])[0]

            subtitle_filename = f'{video_name}{extension}'
            zipf.writestr(subtitle_filename, subtitle)

            if text_corrected[i-1] is not None:
                text_filename= f'{video_name}{extension2}'
                zipf.writestr(text_filename,text_corrected[i-1])

    return zip_filename

                               
@app.route('/download/<filename>')
def download_zip(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)


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

@app.errorhandler(413)
def handle_max_file_size(e):
    return e.description,413

@app.errorhandler(requests.exceptions.ChunkedEncodingError)
def handle_brute_desconection_with_backend():
    global sse_connection_with_backend
    sse_connection_with_backend=None

@app.route('/healthcheck')
def healthcheck():
    return 'OK', 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,threaded=True,debug=False)
    
