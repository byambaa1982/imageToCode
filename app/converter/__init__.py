# app/converter/__init__.py
"""Converter blueprint."""

from flask import Blueprint

converter = Blueprint('converter', __name__)

from app.converter import routes
