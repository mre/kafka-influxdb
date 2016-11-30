FROM python:2.7
MAINTAINER Matthias Endler <matthias-endler@gmx.net>

RUN apt-get update \
    && apt-get install -y git \
    && git clone https://github.com/edenhill/librdkafka.git \
    && cd librdkafka \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf librdkafka \
    && apt-get purge -y git \
    && apt-get clean -y \
    && apt-get autoclean -y \
    && apt-get autoremove -y \
    && rm -rf /var/cache/debconf/*-old \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/share/doc/* \
    && rm -rf /usr/local/manual/mod \
    && rm -rf /usr/local/manual/programs \
    && rm -rf /usr/share/vim/*/doc

ADD . /kafka-influxdb
WORKDIR /kafka-influxdb
RUN python setup.py install
CMD ["./docker/run.sh"]
