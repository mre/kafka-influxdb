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
            # TODO: make this faster?
            metric_range -= 1
            while metric_range >= 0:
                template = self.templates.get(metric_range)
                if template and template.endswith('*'):
                    return template
                metric_range -= 1
        return None

    def apply_template(self, metric_name, template):
        if not template:
            return metric_name.replace('.', self.separator)
        tag_names, template_range = self.tag_names[template]
        metric_parts = metric_name.split('.', template_range)
        measurement = metric_parts.pop().replace('.', self.separator)
        tags = ','.join(['%s=%s' % (tag, value)
            for tag, value in zip(tag_names, metric_parts)])
        if tags:
            return '%s,%s' % (measurement, tags)
        return measurement
