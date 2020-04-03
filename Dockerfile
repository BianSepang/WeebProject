# We're using Alpine Edge
FROM alpine:edge

#
# We have to uncomment Community repo for some packages
#
RUN sed -e 's;^#http\(.*\)/edge/community;http\1/edge/community;g' -i /etc/apk/repositories

#
# Installing Packages
#
RUN apk add --no-cache=true --update \
    coreutils \
    bash \
    build-base \
    bzip2-dev \
    curl \
    gcc \
    g++ \
    git \
    sudo \
    util-linux \
    libevent \
    jpeg-dev \
    libffi-dev \
    libpq \
    libwebp-dev \
    libxml2 \
    libxml2-dev \
    libxslt-dev \
    linux-headers \
    musl \
    openssl-dev \
    openssl \
    wget \
    python \
    python-dev \
    python3 \
    python3-dev \
    readline-dev \
    zlib-dev \
    jpeg \
    zip \
    freetype-dev

RUN python3 -m ensurepip \
    && pip3 install --upgrade pip setuptools \
    && rm -r /usr/lib/python*/ensurepip && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi

RUN pip3 install heroku3 telethon && rm -r /root/.cache

#
# Clone repo and prepare working directory
#
RUN git clone -b master-fallback https://github.com/adekmaulana/ProjectBish /home/projectbish/
WORKDIR /home/projectbish/

#
# Install requirements
#
CMD ["python3","-m","userbot"]
