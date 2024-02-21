# Usa Ubuntu 22.04 como la imagen base
FROM ubuntu:22.04

# Actualiza e instala las dependencias necesarias
RUN apt-get update && apt-get install -y \
    python3-pip\
    ffmpeg

# Define el directorio de trabajo predeterminado
WORKDIR /app

# Copia todo el contenido excepto lo especificado en .dockerignore
COPY . .


RUN pip install torch torchaudio
RUN pip install srt languagecodes numpy configparser tqdm ffmpeg-python
RUN pip install deepgram-sdk==2.5.0  deepl
RUN apt autoclean
    
