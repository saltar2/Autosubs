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

#instalamos dependencias

#RUN pip3 install srt languagecodes numpy configparser tqdm ffmpeg-python
#RUN pip3 install deepgram-sdk==2.5.0  deepl
RUN pip3 install -r requirements.txt
RUN pip3 install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN apt autoclean
#Pre-descargamos el modelo de silero
RUN python3 -c "import torch; torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', onnx=False)" 

    
