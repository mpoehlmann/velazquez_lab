import shlex
from subprocess import Popen

def load_jupyter_server_extension(nbapp):
    """Serve the Dash application."""
    Popen(shlex.split("python app.py --binder"))