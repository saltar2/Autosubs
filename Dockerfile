# Usa Ubuntu 22.04 como la imagen base
FROM ubuntu:22.04

# Actualiza e instala las dependencias necesarias
RUN apt-get update && apt-get install -y \
    python3-pip\
    ffmpeg\
    git\
    automake\
    autoconf\
    libtool && apt autoclean

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
    && cd rnnoise \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install



COPY requirements.txt .
RUN pip3 install -r requirements.txt
#RUN pip3 install spacy

RUN python3 -m spacy download es_dep_news_trf

WORKDIR /app
# Copia todo el contenido excepto lo especificado en .dockerignore
COPY . .


