FROM ubuntu:16.04

ENV LANG="C.UTF-8"

RUN echo "deb mirror://mirrors.ubuntu.com/mirrors.txt xenial main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb mirror://mirrors.ubuntu.com/mirrors.txt xenial-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb mirror://mirrors.ubuntu.com/mirrors.txt xenial-security main restricted universe multiverse" >> /etc/apt/sources.list && \
    apt update && apt-get install -y --no-install-recommends \
        build-essential \
        python3 \
        python3-dev \
        python3-pip \
        python3-setuptools \
        openssh-client \
        openssl \
        libssl-dev \
        libasound2-plugins \
        libsox-fmt-all \
        libsox-dev \
        ffmpeg \
        sox \
        && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 --no-cache-dir install --upgrade pip \
        numpy==1.12.1

RUN mkdir -p /app/software
RUN mkdir -p /app/data/lm
RUN mkdir /app/data/graph
RUN mkdir /app/data/spell

COPY software/kenlm.zip /app/software/kenlm.zip

RUN pip3 --no-cache-dir install six librosa /app/software/kenlm.zip

# setup native client
COPY software/native_client.tar.xz /app/software/native_client.tar.xz
WORKDIR /app/software
RUN tar xvfJ native_client.tar.xz
RUN cp lib* /usr/local/lib/
RUN cp deepspeech /usr/local/bin/
RUN ldconfig

# copy python data files and scripts
COPY ./data/lm/lm.binary /app/data/lm/lm.binary
COPY ./data/graph/output_graph.pb /app/data/graph/output_graph.pb
COPY ./data/spell/words.txt /app/data/spell/words.txt
COPY ./app /app

WORKDIR /app

# build: docker build -t dsclient .
# run  : cat app/data/1284-1180-0010.wav | docker run --rm -i dsclient
ENTRYPOINT ["/app/stt.py"]
