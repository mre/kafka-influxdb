FROM pypy:3
MAINTAINER Matthias Endler <matthias-endler@gmx.net>

ADD . /kafka-influxdb
WORKDIR /kafka-influxdb
RUN pypy3 setup.py install
CMD ["./docker/run.sh"]