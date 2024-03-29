# FROM public.ecr.aws/unocha/alpine-base-s6:3.12
FROM public.ecr.aws/unocha/python3-base-s6:3.9.5


ENV HDX_USER_AGENT=HDXINTERNAL_GEOPREVIEW

WORKDIR /srv/gislayer

COPY . .

RUN mkdir -p /etc/services.d/gislayer && mv docker/run_gislayer /etc/services.d/gislayer/run && \
    apk add --update-cache \
        gdal \
        gdal-tools \
        gettext && \
    apk add --virtual .build-deps \
        build-base \
        git \
        python3-dev \
        postgresql-dev && \
    pip3 install -r requirements.txt && \
    apk del .build-deps && \
    rm -rf /var/lib/apk/* && rm -r /root/.cache
