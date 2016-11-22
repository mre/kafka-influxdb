"""
Maintains a dictionary of valid Graphite message templates.
See: https://github.com/influxdata/influxdb/tree/master/services/graphite
"""


class Template(object):
    """
    Create a lookup dictionary for quick template access (e.g. by an encoder)

    Definitions:
        metric-name: first part if a Graphite message
        metric-range: number of dots '.' in a metric-name

    Templates matching a given Graphite message must have the same
    metric-range. metric-names match on shorter templates if a templates
    ends with a wildcard '*'. More specific templates match first.
    """
    def __init__(self, templates, separator='_'):
        """
        templates: sequence of strings
        """
        self.templates = {}
        self.tag_names = {}
        for template in templates:
            length = template.count('.')
            self.templates[length] = template
            template_parts = template.split('.')[:-1]
            self.tag_names[template] = (template_parts, len(template_parts))
        self.max_template_range = self._init_wildcards()
        self.separator = separator

    def _init_wildcards(self):
        """
        Prepares self.templates for O(1) access in self.get()
        Returns max-key of self.templates
        """
        n = 0
        last_wildcard_template = None
        if self.templates:
            for n in range(max(self.templates.keys()) + 1):
                template = self.templates.get(n)
                if not template:
                    self.templates[n] = last_wildcard_template
                elif template.endswith('*'):
                    last_wildcard_template = template
            n += 1
        self.templates[n] = last_wildcard_template
        return n

    def get_key(self, metric_name):
        """
        Gets a metric-name and returns the measurement with optional
        tags according to the best matching template.
        """
        metric_range = metric_name.count('.')
        template = self.get(metric_range)
        return self.apply_template(metric_name, template)

    def get(self, metric_range):
        """
        Returns the best matching template for the given metric-range.
        """
        try:
            return self.templates[metric_range]
        except KeyError:
            return self.templates[self.max_template_range]

    def apply_template(self, metric_name, template):
        """
        Applies the template to the given metric_name to create the
        measurement with the according tags. Return the measurement.
        """
        if not template:
            return metric_name.replace('.', self.separator)
        tag_names, template_range = self.tag_names[template]
        metric_parts = metric_name.split('.', template_range)
        measurement = metric_parts[-1].replace('.', self.separator)
        tags = ','.join(['%s=%s' % (tag, value)
            for tag, value in zip(tag_names, metric_parts)])
        if tags:
            return '%s,%s' % (measurement, tags)
        return measurement
