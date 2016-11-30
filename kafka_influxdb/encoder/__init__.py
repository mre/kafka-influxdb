import importlib


def load_encoder(protocol, config):
    """
    Creates an instance of the given encoder.
    An encoder converts a message from one format to another
    """
    encoder_module = importlib.import_module("kafka_influxdb.encoder." + protocol)
    encoder_class = getattr(encoder_module, "Encoder")

    template_module = importlib.import_module("kafka_influxdb.template." + protocol)
    template_class = getattr(template_module, "Template")

    # Return an instance of the class
    return encoder_class(template_class(config.templates))
