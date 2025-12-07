# app/payment/__init__.py
"""Payment blueprint."""

from flask import Blueprint

payment = Blueprint('payment', __name__)

from app.payment import routes
