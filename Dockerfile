FROM public.ecr.aws/unocha/python:3.12-stable

ENV HDX_USER_AGENT=HDXINTERNAL_GEOPREVIEW

WORKDIR /srv/gislayer

COPY . .

RUN mkdir -p /etc/services.d/gislayer && mv docker/run_gislayer /etc/services.d/gislayer/run && \
    apk add --update-cache \
    gdal \
    gdal-tools \
    gdal-driver-pg \
    gdal-driver-libkml \
    gettext \
    libpq && \
    apk add --virtual .build-deps \
    build-base \
    git \
    python3-dev \
    postgresql-dev && \
    pip3 install -r requirements.txt && \
    apk del .build-deps && \
    rm -rf /var/lib/apk/* && rm -r /root/.cache

ENTRYPOINT [ "/init" ]
