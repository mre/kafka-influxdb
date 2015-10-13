import importlib

def load_encoder(name):
    """
    Creates an instance of the given encoder.
    An encoder converts a message from one format to another
    """
    modname = "{0}.{1}".format(__package__, name)
    encoder_module = importlib.import_module(modname)
    encoder_class = getattr(encoder_module, "Encoder")
    # Return an instance of the class
    return encoder_class()
