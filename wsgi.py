"""
WSGI Entry Point for PythonAnywhere / Gunicorn Deployment
==========================================================
Usage on PythonAnywhere: point WSGI file to this module
Usage with Gunicorn: gunicorn wsgi:application
"""
import sys
import os

# Add project directory to path (needed for PythonAnywhere)
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from __init__ import create_app

application = create_app()

if __name__ == '__main__':
    application.run()
