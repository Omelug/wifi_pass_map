import re
import logging
log = logging.getLogger(__name__)

def sanitize_filename(filename):
    sanitized_filename = re.sub(r'[^\w\-\.]', '_', filename)
    log.debug(f"Santizied a filename to {sanitize_filename}")
    return sanitized_filename

def source_object_name(name):
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", name))
