import re


def multiple_replacer(*key_values):
    replace_dict = dict(key_values)
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
    return lambda string: pattern.sub(replacement_function, string)


def multiple_replace(string, *key_values):
    return multiple_replacer(*key_values)(string)


def influxdb_tag_escaper():
    return multiple_replacer(('\\', '\\\\'), (' ', '\\ '), (',', '\\,'), ('=', '\\='))
