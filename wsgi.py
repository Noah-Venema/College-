# WSGI entry point for production hosting (e.g. PythonAnywhere).
# The host's WSGI config file should import `application` from this module.
from app import create_app

application = create_app()
