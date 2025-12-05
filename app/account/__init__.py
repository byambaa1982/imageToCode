# app/account/__init__.py
"""Account blueprint."""

from flask import Blueprint

account = Blueprint('account', __name__)

from app.account import routes
