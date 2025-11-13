"""
WSGI entry point for OpenShift deployment
OpenShift S2I requires this file to be named 'wsgi.py'
with an entry point named 'application'
"""
import os
from app import create_app

# Create Flask application instance
# OpenShift requires the entry point to be named 'application'
application = create_app()

if __name__ == '__main__':
    # For local development only
    # OpenShift will use gunicorn to run this application
    port = int(os.environ.get('PORT', 8080))
    application.run(host='0.0.0.0', port=port, debug=False)
