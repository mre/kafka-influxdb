class Encoder(object):
    """
    An encoder for the Collectd JSON format
    See https://collectd.org/wiki/index.php/JSON

    Sample measurements:

    [{"values":[0],"dstypes":["derive"],"dsnames":["value"],"time":1436372292.412,"interval":10.000,"host":"26f2fc918f50","plugin":"cpu","plugin_instance":"1","type":"cpu","type_instance":"interrupt"}]

    [
       {
         "values":  [1901474177],
         "dstypes":  ["counter"],
         "dsnames":    ["value"],
         "time":      1280959128,
         "interval":          10,
         "host":            "leeloo.octo.it",
         "plugin":          "cpu",
         "plugin_instance": "0",
         "type":            "cpu",
         "type_instance":   "idle"
       }
    ]
    """
    def encode(self, msg):
        # Wanna help out here?
        raise NotImplemented
