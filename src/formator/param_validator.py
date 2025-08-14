# If user set input into tool config, it con ve validated by function
# foo(new_param_value) -> bool
import logging
import os

def valid_relative_path(relative_path):
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    abs_path = os.path.join(ROOT_DIR, relative_path)
    print(abs_path)
    if not os.path.exists(abs_path):
        logging.warning(f"Relative path '{relative_path}' does not exist at {abs_path}")
        return False
    return True
