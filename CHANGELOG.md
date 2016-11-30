## Change Log

### master (unreleased)

### v0.8.0 (2016/11/30)

* Update package requirements
* Integrate Confluent Kafka Python client API (with librdkafka support)
* Cleanup setuptools
* Switch from nose to pytest
* Extend travis CI configuration
* Make writing Kafka Readers much more flexible
* Improve error handling in Kafka Reader
* Improve logging messages
* General code cleanup
* Python 3.5 support
* PyPy 5.4 support
* InfluxDB 1.x support
* Deprecate Kafka sample message writer
* Deprecate collectd message writer
* Deprecate builtin benchmark functionality
* Integrate kafkacat for sample message writing
* Improve documentation
* Fix formatting of README for PyPi (thanks @di)
* Update Docker-based benchmarks
* Simplify testing by providing a Makefile-based environment
* Start kafka-influxdb with Python optimization (-O flag) by default.

### v0.7.3 (2016/10/14)

* Support for Python 3.x and PyPy 3.x
* Allow use of external encoders
* Switch from SimpleConsumer to KafkaConsumer (huge performance improvement)
* Add version flag
* Fix unit tests for Python 3
* Fix bugs of supporting mutliple fields in one sample; 
* Add initial mypy static type support
* Full changelog: https://github.com/mre/kafka-influxdb/compare/v0.7.2...v0.7.3

### v0.7.2 (2015/10/30)

* Fix values encoded as strings into Influxdb 0.9x (#9)
* Fix boolean commandline flags changed to strings (#8)
* Fix encoding of multiple measurements in one message (#12)
* Cleanup Docker setup
* Update Documentation
* PEP8 formatting
* Full changelog: https://github.com/mre/kafka-influxdb/compare/v0.7.1...v0.7.2

### v0.7.1 (2015/10/20)

* Add requirements.txt to Manifest file to fix pip install
* Full changelog: https://github.com/mre/kafka-influxdb/compare/v0.7.0...v0.7.1

### v0.7.0 (2015/10/18)

* Add support for SSL and UDP connections to InfluxDB
* Fix loading of encoders on pip install
* Update dependencies
* Refactoring, cleanup
* Full changelog: https://github.com/mre/kafka-influxdb/compare/v0.6.0...v0.7.0

### v0.6.0 (2015/10/07)

* Fix a bug where kafka-influxdb stopped consuming messages (See #5)
* Improve config handling: config file parameters get properly overwritten by cli arguments
* Logging output contains exception message
* Refactoring and cleanup
* Full changelog: https://github.com/mre/kafka-influxdb/compare/v0.5.1...v0.6.0

### v0.5.1 (2015/07/20)

* Make the application more robust by handling Kafka disconnect gracefully.
* Increase code coverage
* Fix docker-compose setup by correctly connecting kafka with zookeeper
* Minor refactoring and cleanup
* Full changelog: https://github.com/mre/kafka-influxdb/compare/v0.5.0...v0.5.1

### v0.5.0 (2015/07/14)

* Create setuptools package
* Add continuous integration
* Full changelog: https://github.com/mre/kafka-influxdb/compare/v0.4.1...v0.5.0

### v0.4.1 (2015/07/13)

* Add functionality for benchmarks and statistics
* Improve Docker test setup
* Performance improvements
* Downloads
* Full changelog: https://github.com/mre/kafka-influxdb/compare/v0.4.0...v0.4.1

### v0.4.0 (2015/07/10)

* Major rewrite which supports InfluxDB 0.9.1
* Supports custom encodings for all input and output formats
* Better error handling
* Updated documentation
* Add unit tests
* Add a license
* Update dependencies
* Add sample configurations for Collectd and InfluxDB
* Complete docker setup for easier testing
* Full changelog: https://github.com/mre/kafka-influxdb/compare/v0.3.0...v0.4.0

### v0.3.0 (2015/03/25)

* Support Influxdb versions 0.8 and 0.9
* Support json format for incoming data
* Full changelog: https://github.com/mre/kafka-influxdb/compare/1f1810c57d61a193e10b9221d83ae14bb988cb57...v0.3.0
