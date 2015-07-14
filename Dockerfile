FROM python:2.7
ADD . /code
WORKDIR /code
RUN python setup.py install
CMD ["./run.sh"]
