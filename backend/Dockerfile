# Usa Ubuntu 22.04 como la imagen base
#FROM ubuntu:22.04
FROM python:3.10-buster

# Actualiza e instala las dependencias necesarias
RUN apt-get update && apt-get install -y \
    python3-pip\
    ffmpeg\
    git\
    automake\
    autoconf\
    libtool\
    build-essential \
    wget && apt autoclean

# Define el directorio de trabajo predeterminado
WORKDIR /app

#instalamos dependencias

#RUN pip3 install srt languagecodes numpy configparser tqdm ffmpeg-python
#RUN pip3 install deepgram-sdk==2.5.0  deepl

#RUN pip3 install -r requirements.txt
RUN pip3 install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

#Pre-descargamos el modelo de silero
RUN python3 -c "import torch; torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', onnx=False)" 

#RUN apt-get install -y git automake autoconf libtool

#denoiser
# Clona el repositorio rnnoise, configura y compila
RUN git clone https://github.com/xiph/rnnoise.git \
#RUN git clone --branch v0.2 https://github.com/xiph/rnnoise.git \
    && cd rnnoise \
    && ./autogen.sh \
    && ./configure \
    && make  -j4 \
    && make -j4 install 



COPY requirements.txt .
RUN pip3 install -r requirements.txt
#RUN pip3 install spacy

#RUN python3 -m spacy download es_dep_news_trf
RUN python3 -m spacy download es_core_news_sm

WORKDIR /app
# Copia todo el contenido excepto lo especificado en .dockerignore
COPY . .

CMD ["python3", "app.py"]
