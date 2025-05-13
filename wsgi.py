import sys

# Add your project directory to the sys.path
path = '/home/yourusername/STEM'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application  # noqa

# This is the PythonAnywhere WSGI configuration file
