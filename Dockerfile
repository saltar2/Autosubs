# Usa Ubuntu 22.04 como la imagen base
FROM ubuntu:22.04

# Actualiza e instala las dependencias necesarias
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    python3-pip\
    ffmpeg

# Agrega el repositorio de deadsnakes PPA para obtener Python 3.9
RUN add-apt-repository ppa:deadsnakes/ppa

# Vuelve a actualizar los repositorios después de agregar el nuevo PPA
RUN apt-get update

# Descarga Python 3.9 desde la fuente
RUN wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz -O /tmp/python.tgz

# Extrae el archivo tar
RUN tar -xf /tmp/python.tgz -C /tmp/

# Navega al directorio de Python 3.9
WORKDIR /tmp/Python-3.9.18

# Configura y compila Python
RUN ./configure --enable-optimizations && \
    make -j $(nproc) && \
    make install

# Limpia el cache y directorios temporales
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Establece la versión de Python como predeterminada
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.9 1

# Establece pip como predeterminado
RUN update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3 1

# Verifica la instalación
RUN python3 --version && pip --version

# Define el directorio de trabajo predeterminado
WORKDIR /app

# Copia todo el contenido excepto lo especificado en .dockerignore
COPY . .


    
