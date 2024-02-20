import gdown

# URL de la carpeta compartida de Google Drive con enlace publico
folder_url = "https://drive.google.com/drive/folders/1mbM8RAEhgnfdh5rXikDEh-PlP6KdDkN2?usp=sharing"

# Descargar todos los archivos y carpetas de la carpeta
gdown.download_folder(folder_url)


