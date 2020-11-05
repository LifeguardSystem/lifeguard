"""
Export application for gunicorn
"""

from lifeguard.validations import load_validations
from lifeguard.server import APP as application

load_validations()
