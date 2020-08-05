FROM unocha/alpine-base-s6:3.12

ENV HDX_USER_AGENT=HDXINTERNAL_GEOPREVIEW

WORKDIR /srv/gislayer

COPY . .

RUN mkdir -p /etc/services.d/gislayer && mv docker/run_gislayer /etc/services.d/gislayer/run && \
    apk add --update-cache \
        python3 \
        py3-pip \
        gdal \
        gdal-tools \
        gettext \
        libpq && \
    apk add --virtual .build-deps build-base python3-dev postgresql-dev && \
    pip3 install -r requirements.txt && \
    apk del .build-deps && rm -rf /var/lib/apk/* && rm -r /root/.cache
