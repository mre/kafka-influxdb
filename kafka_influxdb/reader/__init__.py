import importlib


def load_reader(name, host, port, group, topic):
    """
    Creates an instance of the given reader.
    An reader consumes messages from Kafka.
    """
    reader_module = importlib.import_module(name)
    reader_class = getattr(reader_module, "Reader")
    # Return an instance of the class
    return reader_class(host, port, group, topic)
