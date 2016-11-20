"""
Maintains a dictionary of valid Graphite message templates.

Templates allow matching parts of a metric name to be used as tag keys in the stored metric.
They have a similar format to Graphite metric names.
The values in between the separators are used as the tag keys.
The location of the tag key that matches the same position as the Graphite metric section
is used as the value.
If there is no value, the Graphite portion is skipped.

Example:
Graphite input: servers.localhost.cpu.loadavg.10
Template:       host.resource.measurement*
Output:         measurement=loadavg.10 tags=host=localhost resource=cpu

See: https://github.com/influxdata/influxdb/tree/master/services/graphite
"""
from collections import defaultdict


class Template(object):
    """
    Create an O(1) lookup dictionary for quick template access (e.g. by an encoder)
    """
    def __init__(self, templates):
        d = {}
        for template in templates:
            length = template.count('.')
            d[length] = template
        self.templates = d

    def get(self, key):
        try:
            return self.templates[key]
        except KeyError:
            key -= 1
            while key >= 0:
                template = self.templates.get(key)
                if template and template.endswith('*'):
                    return template
                key -= 1
        return None
