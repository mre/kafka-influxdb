FROM python
LABEL maintainer="Matthias Endler <matthias-endler@gmx.net>"

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "-m", "kafka_influxdb" ]