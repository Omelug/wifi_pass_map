import logging
import sys
import os
from io import StringIO
from unittest.mock import patch

base_dir =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(base_dir, "src")
sys.path.insert(0, src_path)

from app import create_app


def before_all(context):
    import logging
    import sys
    import os
    from io import StringIO

    sys.path.insert(0, os.path.abspath("src"))
    from app import create_app

    context.app = create_app()
    context.client = context.app.test_client()
    # Set up log capture for root logger
    context.log_stream = StringIO()
    context.log_handler = logging.StreamHandler(context.log_stream)
    context.log_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(context.log_handler)  # Attach to root logger
    logging.getLogger().setLevel(logging.DEBUG)

def after_all(context):
    if hasattr(context, "log_handler"):
        logging.getLogger().removeHandler(context.log_handler)
    context.app = None


def before_scenario(context, scenario):
    if "wigle_mock" in scenario.tags:
        patcher = patch('src.map_app.sources.wigle.requests.get')
        context.mock_get = patcher.start()
        context._requests_get_patcher = patcher

def after_scenario(context, scenario):
    if "wigle_mock" in scenario.tags:
        if hasattr(context, '_requests_get_patcher'):
            context._requests_get_patcher.stop()