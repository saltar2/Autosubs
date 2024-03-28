from flask import Flask, render_template, request, redirect, url_for, send_file
import os, requests
from werkzeug.utils import secure_filename
import zipfile
# Ruta para la subida de archivos
from flask import Response, stream_with_context

# Configuración de la aplicación
app = Flask(__name__)

#docker url
url_base='http://backend:5001'
#local url
#url_base='http://localhost:5001'
# Configuración de la subida de archivos
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'm4v', 'mts', 'wmv', 'mpg', 'flv'}
app.config['MAX_CONTENT_LENGTH'] = 2048 * 1024 * 1024  # Permitimos 2 GB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

# Función para verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para la página de inicio
@app.route('/')
def index():
    # Obtener los códigos de idioma del backend
    backend_url = url_base + '/language_codes'
    response = requests.get(backend_url)
    language_codes = response.json()

    # Renderizar la página de inicio con los códigos de idioma
    return render_template('index.html', language_codes=language_codes)


'''@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Obtener los archivos y el idioma del formulario
        uploaded_files = request.files.getlist('file')
        lan = request.form.get('language')

        # Variables para el progreso y la lista de subtítulos
        total_files = len(uploaded_files)
        uploaded_count = 0
        subs = []

        # Generar eventos SSE para informar sobre el progreso
        def generate(file):
            nonlocal uploaded_count
            if file and allowed_file(file.filename):
                # Guardar el archivo
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_count += 1

                # Actualizar el progreso de la carga
                progress = int((uploaded_count / total_files) * 100)

                # Enviar el progreso a través de SSE
                yield f"""data: {{"fileName": "{filename}", "progress": {progress}}}"""


                # Enviar el archivo al backend
                backend_url = url_base + '/process_video'
                files = {'file': (filename, open(filepath, 'rb').read(), file.mimetype)}
                data = {'language': lan}
                response = requests.post(backend_url, data=data, files=files)

                # Obtener el subtítulo del backend
                subtitle = response.json()

                # Agregar el subtítulo a la lista
                subs.append(subtitle)

                # Eliminar el archivo temporal
                os.remove(filepath)

        # Retornar la respuesta con SSE
        return Response(stream_with_context(generate(file) for file in uploaded_files), content_type='text/event-stream')

    except requests.exceptions.RequestException as e:
        # Manejar errores de comunicación con el backend
        return render_template('error.html', error_message=f"Error procesando archivos: {str(e)}"), 500
    except Exception as e:
        # Manejar otros errores inesperados
        return render_template('error.html', error_message=f"An unexpected error occurred: {str(e)}"), 500'''

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Obtener los archivos y el idioma del formulario
        uploaded_files = request.files.getlist('file')
        lan = request.form.get('language')

        # Variables para el progreso y la lista de subtítulos
        total_files = len(uploaded_files)
        uploaded_count = 0
        subs = []

        # Procesar cada archivo
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                # Guardar el archivo
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_count += 1

                # Actualizar el progreso de la carga
                progress = int((uploaded_count / total_files) * 100)

                # Enviar el archivo al backend
                backend_url = url_base + '/process_video'
                files = {'file': (filename, open(filepath, 'rb').read(), file.mimetype)}
                data = {'language': lan}
                response = requests.post(backend_url, data=data, files=files)

                # Obtener el subtítulo del backend
                subtitle = response.json()

                # Agregar el subtítulo a la lista
                subs.append(subtitle)

                # Eliminar el archivo temporal
                os.remove(filepath)

        # Generar archivo ZIP con los subtítulos
        zip_filename = 'subtitles.zip'
        extension = ".es.srt"
        with zipfile.ZipFile(os.path.join(app.config['DOWNLOAD_FOLDER'], zip_filename), 'w') as zipf:
            for i, subtitle in enumerate(subs, start=1):
                video_name = os.path.splitext(uploaded_files[i - 1].filename)[0]  # Obtener el nombre del video sin la extensión
                subtitle_filename = f'{video_name}{extension}'  # Crear el nombre del archivo de subtítulo
                zipf.writestr(subtitle_filename, subtitle)

        # Generar la URL de descarga
        zip_url = url_for('download_zip', filename=zip_filename)

        # Retornar la URL de descarga
        return zip_url
    except requests.exceptions.RequestException as e:
        # Manejar errores de comunicación con el backend
        return render_template('error.html', error_message=f"Error procesando archivos: {str(e)}"), 500
    except Exception as e:
        # Manejar otros errores inesperados
        return render_template('error.html', error_message=f"An unexpected error occurred: {str(e)}"), 500
                               
@app.route('/download/<filename>')
def download_zip(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=False)
