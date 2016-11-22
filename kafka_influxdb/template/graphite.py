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
        d = {}
        self.tag_names = {}
        for template in templates:
            length = template.count('.')
            d[length] = template
            template_parts = template.split('.')[:-1]
            self.tag_names[template] = (template_parts, len(template_parts))

        if templates:
            last_wildcard_template = None
            for n in range(max(d.keys()) + 1):
                template = d.get(n)
                if not template:
                    d[n] = last_wildcard_template
                elif template.endswith('*'):
                    last_wildcard_template = template
            n += 1
            d[n] = last_wildcard_template
        else:
            n = 0
        self.max_template_range = n
        d[self.max_template_range] = d.get(self.max_template_range)

        self.templates = d
        self.separator = separator

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

    #@profile
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
