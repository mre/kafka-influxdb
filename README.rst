Kafka-InfluxDB
==============

|PyPi Version| |Build Status| |Coverage Status| |Code Climate| |Downloads| |Python Versions| |Scrutinizer|


| A Kafka consumer for InfluxDB written in Python.
| All messages sent to Kafka on a certain topic will be relayed to Influxdb.
| Supports InfluxDB 0.9.x and up. For InfluxDB 0.8.x support, 
| check out the `0.3.0 tag <https://github.com/mre/kafka-influxdb/tree/v0.3.0>`__.


Use cases
---------

Kafka will serve as a buffer for your metric data during high load.
Also it's useful for metrics from offshore data centers with unreliable connections to your monitoring backend.

.. figure:: https://raw.githubusercontent.com/mre/kafka-influxdb/master/assets/schema-small.png
   :alt: Usage example


Quickstart
----------

To run the tool from your local machine:

::

    pip install kafka_influxdb
    kafka_influxdb -c config-example.yaml


Benchmark
---------

To see the tool in action, you can start a complete
``CollectD -> Kafka -> kafka_influxdb -> Influxdb`` setup with the
following command:

::

    docker-compose up

This will immediately start reading messages from Kafka and write them
into InfluxDB. To see the output, you can use the InfluxDB Admin Interface.
Check on which port it is running with ``docker ps | grep tutum/influxdb``.
There should be a mapping like 32785->8083/tcp or so.
In this case 32785 is the port where you can reach it.
Then go to ``http://<docker_host_ip>:<port>`` and type ``SHOW MEASUREMENTS``
to see the output. (``<docker_host_ip>`` is probably ``localhost`` on Linux.
On Mac you can find out with ``boot2docker ip`` or ``docker-machine ip``).

By default this will write 1.000.000 sample messages into the
``benchmark`` Kafka topic. After that it will consume the messages again
to measure the throughput. Sample output using the above Docker setup
inside a virtual machine:

::

    Flushing output buffer. 10811.29 messages/s
    Flushing output buffer. 11375.65 messages/s
    Flushing output buffer. 11930.45 messages/s
    Flushing output buffer. 11970.28 messages/s
    Flushing output buffer. 11016.74 messages/s
    Flushing output buffer. 11852.67 messages/s
    Flushing output buffer. 11833.07 messages/s
    Flushing output buffer. 11599.32 messages/s
    Flushing output buffer. 11800.12 messages/s
    Flushing output buffer. 12026.89 messages/s
    Flushing output buffer. 12287.26 messages/s
    Flushing output buffer. 11538.44 messages/s

For higher performance you can run kafka-influxdb on **PyPy3**. Currently this gives me **around 50.000 msgs/s in my benchmarks**.



Supported formats
-----------------

| You can write a custom encoder to support any input and output format (even fancy things like Protobuf). Look at the examples inside the ``encoder`` directory to get started. The following formats are officially supported:

Input formats
~~~~~~~~~~~~~

-  `Collectd Graphite ASCII format <https://collectd.org/wiki/index.php/Graphite>`_:
::

   mydatacenter.myhost.load.load.shortterm 0.45 1436357630

-  `Collectd JSON format <https://collectd.org/wiki/index.php/JSON>`_:
.. code-block:: json

  [{
      "values":[
         0.6
      ],
      "dstypes":[
         "gauge"
      ],
      "dsnames":[
         "value"
      ],
      "time":1444745144.824,
      "interval":10.000,
      "host":"xx.example.internal",
      "plugin":"cpu",
      "plugin_instance":"1",
      "type":"percent",
      "type_instance":"system"
   }]


Output formats
~~~~~~~~~~~~~~

-  `InfluxDB 0.9.x line protocol format <https://influxdb.com/docs/v0.9/write_protocols/line.html>`_:
::

   load_load_shortterm,datacenter=mydatacenter,host=myhost value="0.45" 1436357630

-  `InfluxDB 0.8.x JSON format <https://influxdb.com/docs/v0.8/api/reading_and_writing_data.html#writing-data-through-http>`_ (deprecated)


Configuration
-------------

| Take a look at the ``config-example.yaml`` to find out how to create a config file.
| You can overwrite the settings from the commandline. The following parameters are allowed:

========================================================= =================================================================================================
Option                                                    Description
========================================================= =================================================================================================
``-h``, ``--help``                                        Show help message and exit
``--kafka_host KAFKA_HOST``                               Hostname or IP of Kafka message broker (default: localhost)
``--kafka_port KAFKA_PORT``                               Port of Kafka message broker (default: 9092)
``--kafka_topic KAFKA_TOPIC``                             Topic for metrics (default: my_topic)
``--kafka_group KAFKA_GROUP``                             Kafka consumer group (default: my_group)
``--influxdb_host INFLUXDB_HOST``                         InfluxDB hostname or IP (default: localhost)
``--influxdb_port INFLUXDB_PORT``                         InfluxDB API port (default: 8086)
``--influxdb_user INFLUXDB_USER``                         InfluxDB username (default: root)
``--influxdb_password INFLUXDB_PASSWORD``                 InfluxDB password (default: root)
``--influxdb_dbname INFLUXDB_DBNAME``                     InfluxDB database to write metrics into (default: metrics)
``--influxdb_use_ssl``                                    Use SSL connection for InfluxDB (default: False)
``--influxdb_verify_ssl``                                 Verify the SSL certificate before connecting (default: False)
``--influxdb_timeout INFLUXDB_TIMEOUT``                   Max number of seconds to establish a connection to InfluxDB (default: 5)
``--influxdb_use_udp``                                    Use UDP connection for InfluxDB (default: False)
``--influxdb_retention_policy INFLUXDB_RETENTION_POLICY`` Retention policy for incoming metrics (default: default)
``--influxdb_time_precision INFLUXDB_TIME_PRECISION``     Precision of incoming metrics. Can be one of 's', 'm', 'ms', 'u' (default: s)
``--encoder ENCODER``                                     Input encoder which converts an incoming message to dictionary (default: collectd_graphite_encoder)
``--buffer_size BUFFER_SIZE``                             Maximum number of messages that will be collected before flushing to the backend (default: 1000)
``-c CONFIGFILE``, ``--configfile CONFIGFILE``            Configfile path (default: None)
``-s``, ``--statistics``                                  Show performance statistics (default: True)
``-b``, ``--benchmark``                                   Run benchmark (default: False)
``-v``, ``--verbose``                                     Set verbosity level. Increase verbosity by adding a v: -v -vv -vvv (default: 0)
``--version``                                             Show version
========================================================= =================================================================================================


Alternatives
------------

There is a Kafka input plugin and an InfluxDB output plugin for logstash.
Currently InfluxDB 0.9 support is not part of the official logstash Influxdb output plugin
(see `this issue <https://github.com/logstash-plugins/logstash-output-influxdb/issues/24>`__ and `this pull request <https://github.com/logstash-plugins/logstash-output-influxdb/pull/29>`__)

There is a fork which supports Influxdb 0.9 and also allows us to set the InfluxDB measurement name from a field in the graphite string.
We've achieved a message throughput of around 5000 messages/second with that setup. Check out the configuration at `contrib/logstash/config.conf`.
You can run the benchmark yourself:

::

   # Start the logstash docker-compose setup
   docker-compose -f docker-compose-logstash.yml up -d
   # Open an interactive shell to the logstash container
   docker exec -it kafkainfluxdb_logstash_1 bash
   # Run the benchmark
   ./run.sh



Please send a Pull Request if you know of other tools that can be mentioned here.


.. |Build Status| image:: https://travis-ci.org/mre/kafka-influxdb.svg?branch=master
   :target: https://travis-ci.org/mre/kafka-influxdb
.. |Coverage Status| image:: https://coveralls.io/repos/mre/kafka-influxdb/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/mre/kafka-influxdb?branch=master
.. |Code Climate| image:: https://codeclimate.com/github/mre/kafka-influxdb/badges/gpa.svg
   :target: https://codeclimate.com/github/mre/kafka-influxdb
   :alt: Code Climate
.. |PyPi Version| image:: https://badge.fury.io/py/kafka_influxdb.svg
   :target: https://badge.fury.io/py/kafka_influxdb
.. |Downloads| image:: https://img.shields.io/pypi/dd/kafka-influxdb.svg
   :target: https://pypi.python.org/pypi/kafka-influxdb/
   :alt: pypi downloads per day
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/kafka-influxdb.svg
   :target: https://pypi.python.org/pypi/coveralls/
   :alt: Supported Python Versions
.. |Scrutinizer| image:: https://scrutinizer-ci.com/g/mre/kafka-influxdb/badges/quality-score.png?b=master
   :target: https://scrutinizer-ci.com/g/mre/kafka-influxdb/?branch=master
   :alt: Scrutinizer Code Quality  
