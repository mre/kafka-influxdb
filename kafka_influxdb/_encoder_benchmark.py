"""
Benchmarking for graphite-encoder module.
"""
import timeit

from encoder.graphite import Encoder
from template.graphite import Template


loops = int(1e2)
messages = (
    b'dus.www0.cpu.shortterm',
    b'562987602.cpu.load.longterm',
    b'hkg.cpu.load.load.pipapo',
    b'what.ever.you.like.here',
)

templates = (
    'load.measurement*',
    'direkt.match.by.five.measurement',
)


def run_benchmark():
    template = Template(templates)
    encoder = Encoder(Template)
    start = timeit.default_timer()

    for n in range(loops):
        for message in messages:
            result = encoder.encode(message)

    stop = timeit.default_timer()
    delta = stop - start
    calls = len(messages) * loops
    encodings_per_sec = calls / delta

    print('calls  :{:14}'.format(calls))
    print('runtime:{:14.2f} sec'.format(delta))
    print('1/sec  :{:14.2f}'.format(encodings_per_sec))


if __name__ == '__main__':
    run_benchmark()

