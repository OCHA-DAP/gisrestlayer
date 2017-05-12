FROM unocha/hdx-gislayer:THISTAG

COPY run_gisworker /srv/

RUN rm -rf /etc/services.d/gislayer && \
    mkdir -p /etc/services.d/gisworker && \
    mv /srv/run_gisworker /etc/services.d/gisworker/run
