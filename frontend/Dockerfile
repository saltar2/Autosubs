# Usa una imagen de Python como base
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias necesarias
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y wget
# Expone el puerto 5000 para acceder a la aplicación Flask
EXPOSE 5000

# Copia el contenido del directorio frontend al directorio de trabajo en el contenedor
COPY . .

# Define el comando para ejecutar la aplicación Flask
CMD ["python", "app.py"]
