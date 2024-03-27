from flask import Flask, render_template, request, redirect, url_for,send_file
import os,requests
from werkzeug.utils import secure_filename
import zipfile
#from ..backend.main import language_codes

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER='downloads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'm4v', 'mts', 'wmv', 'mpg', 'flv'}
#docker url
#url_base='http://backend:5001'
#local url
url_base='http://localhost:5001'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    backend_url = url_base+'/language_codes'
    response = requests.get(backend_url)
    language_codes = response.json()
    return render_template('index.html',language_codes=language_codes)

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist('file')
    lan = request.form.get('language')
    total_files = len(uploaded_files)
    uploaded_count = 0
    subs=[]
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded_count += 1

            # Actualizar el progreso de la carga
            progress = int((uploaded_count / total_files) * 100)

            # Enviar el archivo al backend
            backend_url = url_base+'/process_video'
            files = {'file':  (filename,file.read())}  # Pasar el archivo directamente
            data = {'language': lan}
            response = requests.post(backend_url, files=files, data=data)

            subtitle=response.json()

            subs.append(subtitle)
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.remove(filepath)
    # Generar archivo ZIP con los subtítulos
    zip_filename = 'subtitles.zip'
    extension=".es.srt"
    with zipfile.ZipFile(os.path.join(app.config['DOWNLOAD_FOLDER'], zip_filename), 'w') as zipf:
        for i, subtitle in enumerate(subs, start=1):
            video_name = os.path.splitext(uploaded_files[i - 1].filename)[0]  # Obtener el nombre del video sin la extensión
            subtitle_filename = f'{video_name}{extension}'  # Crear el nombre del archivo de subtítulo
            zipf.writestr(subtitle_filename, subtitle)



    zip_url = url_for('download_zip', filename=zip_filename)
    return zip_url

@app.route('/download/<filename>')
def download_zip(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
