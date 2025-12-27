# app/launch/__init__.py
"""Launch management blueprint."""

from flask import Blueprint

launch = Blueprint('launch', __name__, url_prefix='/launch')

from app.launch import routes
