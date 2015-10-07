Kafka-InfluxDB
==============

|Build Status| |Coverage Status|

| A Kafka consumer for InfluxDB written in Python.
| All messages sent to Kafka on a certain topic will be relayed to Influxdb.
| Supports InfluxDB 0.9.x. For InfluxDB 0.8.x support, check out the `0.3.0 tag <https://github.com/mre/kafka-influxdb/tree/v0.3.0>`__.


Use cases
---------

Kafka can serve as a buffer for your metric data during high load or read metrics from offshore data centers.
Imagine the following scenario:

.. figure:: assets/schema-small.png
   :alt: Usage example


Quick start
-----------

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

Run on your local machine
-------------------------

If you want to run a local instance, you can do so with the following
commands:

::

    pip install kafka_influxdb
    # Create a config.yaml like the one in this repository
    kafka_influxdb -c config.yaml

Benchmark
---------

You can use the built-in benchmark tool for performance measurements:

::

    kafka-influxdb -b

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

Supported formats
-----------------

| You can write a custom encoder to support any input and output format (even fancy things like Protobuf).
| Look at the examples in the ``encoder`` folder to get started. For now we support the following formats:

Input formats
~~~~~~~~~~~~~

-  Collectd Graphite, e.g. "mydatacenter.myhost.load.load.shortterm 0.45
   1436357630"

Output formats
~~~~~~~~~~~~~~

-  InfluxDB 0.9.x line protocol output (e.g.
   ``load_load_shortterm,datacenter=mydatacenter,host=myhost value="0.45" 1436357630``)
-  InfluxDB 0.8.x JSON output (deprecated)

Configuration
-------------

| Take a look at the ``config.yaml`` to find out how to create a config file.
| You can overwrite the settings from the commandline with the following flags:

::

    usage: kafka_influxdb.py [-h] [--kafka_host KAFKA_HOST]
                             [--kafka_port KAFKA_PORT] [--kafka_topic KAFKA_TOPIC]
                             [--kafka_group KAFKA_GROUP]
                             [--influxdb_host INFLUXDB_HOST]
                             [--influxdb_port INFLUXDB_PORT]
                             [--influxdb_user INFLUXDB_USER]
                             [--influxdb_password INFLUXDB_PASSWORD]
                             [--influxdb_dbname INFLUXDB_DBNAME]
                             [--influxdb_retention_policy INFLUXDB_RETENTION_POLICY]
                             [--influxdb_time_precision INFLUXDB_TIME_PRECISION]
                             [--encoder ENCODER] [--buffer_size BUFFER_SIZE]
                             [-c CONFIGFILE] [-s] [-b] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      --kafka_host KAFKA_HOST
                            Hostname or IP of Kafka message broker (default:
                            localhost)
      --kafka_port KAFKA_PORT
                            Port of Kafka message broker (default: 9092)
      --kafka_topic KAFKA_TOPIC
                            Topic for metrics (default: my_topic)
      --kafka_group KAFKA_GROUP
                            Kafka consumer group (default: my_group)
      --influxdb_host INFLUXDB_HOST
                            InfluxDB hostname or IP (default: localhost)
      --influxdb_port INFLUXDB_PORT
                            InfluxDB API port (default: 8086)
      --influxdb_user INFLUXDB_USER
                            InfluxDB username (default: root)
      --influxdb_password INFLUXDB_PASSWORD
                            InfluxDB password (default: root)
      --influxdb_dbname INFLUXDB_DBNAME
                            InfluXDB database to write metrics into (default:
                            metrics)
      --influxdb_retention_policy INFLUXDB_RETENTION_POLICY
                            Retention policy for incoming metrics (default:
                            default)
      --influxdb_time_precision INFLUXDB_TIME_PRECISION
                            Precision of incoming metrics. Can be one of 's', 'm',
                            'ms', 'u' (default: s)
      --encoder ENCODER     Input encoder which converts an incoming message to
                            dictionary (default: collectd_graphite_encoder)
      --buffer_size BUFFER_SIZE
                            Maximum number of messages that will be collected
                            before flushing to the backend (default: 1000)
      -c CONFIGFILE, --configfile CONFIGFILE
                            Configfile path (default: None)
      -s, --statistics      Show performance statistics (default: True)
      -b, --benchmark       Run benchmark (default: False)
      -v, --verbose         Set verbosity level. Increase verbosity by adding a v:
                            -v -vv -vvv (default: 0)

TODO
----

-  flush buffer if not full but some time has gone by (safety net for
   low frequency input)
-  Support reading from multiple partitions and topics (using Python
   multiprocessing)
-  Enable settings using environment variables for Docker image

.. |Build Status| image:: https://travis-ci.org/mre/kafka-influxdb.svg?branch=master
   :target: https://travis-ci.org/mre/kafka-influxdb
.. |Coverage Status| image:: https://coveralls.io/repos/mre/kafka-influxdb/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/mre/kafka-influxdb?branch=master
