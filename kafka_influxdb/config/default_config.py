DEFAULT_CONFIG = {
    'kafka': {
        'host': 'localhost',
        'port': '9092',
        'topic': 'my_topic',
        'group': 'kafka-influxdb'
    },
    'influxdb': {
        'host': 'localhost',
        'port': 8086,
        'user': 'root',
        'password': 'root',
        'dbname': 'metrics',
        'use_ssl': False,
        'verify_ssl': False,
        'timeout': 5,
        'use_udp': False,
        'retention_policy': 'default',
        'time_precision': 's'
    },
    'encoder': 'kafka_influxdb.encoder.collectd_graphite_encoder',
    'buffer_size': 1000,
    'configfile': None,
    'c': None,
    'statistics': False,
    's': False,
    'benchmark': False,
    'b': False,
    'verbose': 0,
    'v': 0
}
