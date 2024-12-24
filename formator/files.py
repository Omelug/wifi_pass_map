import re
import logging
log = logging.getLogger(__name__)

def sanitize_filename(filename):
    sanitized_filename = re.sub(r'[^\w\-\.]', '_', filename)
    log.debug(f"Santizied a filename to {sanitize_filename}")
    return sanitized_filename