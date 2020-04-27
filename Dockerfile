FROM unocha/alpine-base-s6-python3:3.11.2

ENV HDX_USER_AGENT=HDXINTERNAL_GEOPREVIEW

WORKDIR /srv/gislayer

COPY . .

RUN pip3 install --upgrade pip setuptools && \
    mkdir -p /etc/services.d/gislayer && mv docker/run_gislayer /etc/services.d/gislayer/run && \
    apk add --update-cache gettext libpq && \
    apk add --virtual .build-deps build-base python3-dev postgresql-dev && \
    pip3 install -r requirements.txt && \
    apk del .build-deps && rm -rf /var/lib/apk/* && rm -r /root/.cache