FROM python:2.7
ADD . /kafka-influxdb
WORKDIR /kafka-influxdb
RUN python setup.py install
CMD ["./run.sh"]
