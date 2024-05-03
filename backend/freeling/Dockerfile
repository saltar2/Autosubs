FROM python:3.8.16-buster AS builder


ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Madrid

RUN echo "******** Installing dependencies... please wait" && \
    apt-get update -qq && \
    apt-get install -qq -y build-essential wget locales cmake \
                           libicu-dev libboost-regex-dev libboost-system-dev \
                           libboost-program-options-dev libboost-thread-dev \
                           libboost-filesystem-dev zlib1g-dev \
                           swig python3-dev default-jdk && \
    ( (echo en_US.UTF-8 UTF-8 >> /var/lib/locales/supported.d/en && locale-gen) || \
      (sed -i 's/^# \(en_US.UTF-8\)/\1/' /etc/locale.gen && locale-gen) || \
      locale-gen en_US.UTF-8 )

RUN export FL_VERSION=4.2 && \
    cd /tmp && \
    echo "******** Downloading FreeLing... please wait" && \
    wget --progress=dot:giga https://github.com/TALP-UPC/FreeLing/releases/download/$FL_VERSION/FreeLing-src-$FL_VERSION.tar.gz && \
    wget --progress=dot:giga https://github.com/TALP-UPC/FreeLing/releases/download/$FL_VERSION/FreeLing-langs-src-$FL_VERSION.tar.gz && \
    echo "******** Uncompressing FreeLing... please wait" && \
    tar xzf FreeLing-src-$FL_VERSION.tar.gz && \
    tar xzf FreeLing-langs-src-$FL_VERSION.tar.gz && \
    rm -rf FreeLing-src-$FL_VERSION.tar.gz FreeLing-langs-src-$FL_VERSION.tar.gz && \
    cd /tmp/FreeLing-$FL_VERSION && \
    mkdir build && \
    cd build && \
    echo "******** Compiling FreeLing... please wait" && \
    cmake .. -DJAVA_API=OFF -DTRACES=ON -DPYTHON3_API=ON -Wno-dev  && \
    make -j2 && \
    echo "******** Installing FreeLing... please wait" && \
#    make -j2 install DCMAKE_INSTALL_PREFIX=$FLINSTALL && \
    make -j2 install && \
#
#   Uncomment to remove unwanted languages data to save space && \
#   rm -rf /usr/local/share/freeling/ru && \
#   rm -rf /usr/local/share/freeling/cy && \
#   rm -rf /usr/local/share/freeling/pt && \
#   etc ....
#
    cd && \
    rm -rf /tmp/FreeLing-$FL_VERSION && \
    apt-get --purge -y remove build-essential libicu-dev \
            libboost-regex-dev libboost-system-dev \
            libboost-program-options-dev libboost-thread-dev \
	        libboost-filesystem-dev zlib1g-dev\
            cmake swig python3-dev && \
    apt-get clean -y #&& \
    rm -rf /var/lib/apt/lists/*         

# RUN echo "deb-src http://deb.debian.org/debian bullseye main" >> /etc/apt/sources.list

RUN apt-get update -qq && \
    apt-get install -qq -y default-libmysqlclient-dev python3-lxml && \
    apt-get clean -y 

# Create app directory
WORKDIR /app

# Install app dependencies

ENV LD_LIBRARY_PATH=/usr/local/share/freeling/APIs/python3
ENV PYTHONPATH=/usr/local/share/freeling/APIs/python3

#RUN pip install lxml
RUN pip install flask

# este fichero pertenece al paquete pattern. Se ha modificado con la conjugación de algunos verbos 
# irregulares.este fichero pertenece al paquete pattern. Se ha modificado con la conjugación de algunos verbos irregulares.

COPY es-verbs.txt /usr/local/lib/python3.8/site-packages/pattern/text/es/

# Bundle app source
COPY app.py ./
#EXPOSE 5002


CMD ["python3", "app.py"]

# CMD echo 'Hello world' | analyze -f en.cfg | grep -c 'world world NN 1'