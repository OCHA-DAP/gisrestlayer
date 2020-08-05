FROM unocha/alpine-base-s6-python3:3.11.2

# echo http://dl-cdn.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories

ENV pkgver=2.2.4

RUN echo http://dl-cdn.alpinelinux.org/alpine/edge/community >> \
        /etc/apk/repositories && \
    apk add --update-cache \
        proj-dev\
        libkml \
        libstdc++ \
        openssh && \
    apk add --virtual .build-deps \
        build-base \
        autoconf \
        automake \
        curl-dev \
        expat-dev \
        git \
        libtool \
        postgresql-dev \
        proj-dev \
        libkml-dev && \
    curl \
        http://download.osgeo.org/gdal/$pkgver/gdal-$pkgver.tar.gz \
        -o /gdal-$pkgver.tar.gz && \
    tar xvzf /gdal-$pkgver.tar.gz && \
    mv gdal-$pkgver gdal && \
    cd gdal && \
    ./configure --with-pg=/usr/bin/pg_config --prefix=/usr --with-libkml=yes && \
    make && \
    make install && \
    cd / && \
    rm -rf /gdal-$pkgver.tar.gz && \
    rm -rf /gdal && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/*
