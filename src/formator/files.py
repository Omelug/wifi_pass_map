import re

def source_object_name(name):
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", name))
