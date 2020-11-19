"""
Export application for gunicorn
"""

from lifeguard import setup
from lifeguard.server import APP as application

setup()
