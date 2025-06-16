import sys
import os

base_dir =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(base_dir, "src")
sys.path.insert(0, src_path)

from app import create_app


def before_all(context):
    #print("[DEBUG] sys.path:", sys.path)
    sys.path.insert(0, os.path.abspath("src"))
    context.app = create_app()
    context.client = context.app.test_client()

def after_all(context):
    context.app = None
