FROM logstash:5.0
MAINTAINER Matthias Endler <matthias-endler@gmx.net>

RUN apt-get update && apt-get install -y git rubygems python python-pip

# Install the logstash Kafka input plugin
RUN /usr/share/logstash/bin/logstash-plugin install logstash-input-kafka \
    && /usr/share/logstash/bin/logstash-plugin install logstash-output-influxdb

ADD . /logstash
WORKDIR /logstash
RUN chmod +x run.sh

CMD ["./run.sh"]
