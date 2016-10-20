try:
    # Test for mypy support (requires Python 3)
    from typing import Text
except ImportError:
    pass

class Encoder(object):
    @staticmethod
    def encode(msg):
        # type: (bytes) -> List[bytes]
        """
        Don't change the message at all
        :param msg:
        """
        return [msg]
