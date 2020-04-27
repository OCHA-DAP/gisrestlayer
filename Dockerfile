FROM unocha/hdx-base-gislayer:alpine

ENV HDX_USER_AGENT=HDXINTERNAL_GEOPREVIEW

WORKDIR /srv/gislayer

COPY . .

#RUN apk add --update-cache
#        python && \
#    python -m ensurepip && \
#    rm -r /usr/lib/python*/ensurepip && \
#    pip install --upgrade pip setuptools && \
#    rm -r /root/.cache && \
#    apk add \
#        gettext \
#        libpq && \
#    apk add --virtual .build-deps \
#        git \
#        postgresql-dev \
#        build-base \
#        python-dev && \
#    pip install -r requirements.txt && \
#    pip install requests && \
#    mkdir -p /etc/services.d/gislayer && \
#    mv docker/run_gislayer /etc/services.d/gislayer/run && \
#    apk del \
#        .build-deps \
#        postgresql-dev \
#        build-base \
#        python-dev && \
#    rm -rf /var/lib/apk/*
RUN apk add --update-cache python3 gettext libpq && pip3 install --upgrade pip setuptools && \
    mkdir -p /etc/services.d/gislayer && \
    mv docker/run_gislayer /etc/services.d/gislayer/run
RUN apk add --virtual .build-deps build-base python3-dev postgresql-dev
RUN pip3 install -r requirements.txt && pip3 install -r dev-requirements.txt
RUN apk del .build-deps && rm -rf /var/lib/apk/* && rm -r /root/.cache