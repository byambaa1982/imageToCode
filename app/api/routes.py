# app/api/routes.py
"""API routes (future implementation)."""

from flask import jsonify
from flask_login import current_user
from app.api import api


@api.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })


@api.route('/cart/count')
def cart_count():
    """
    Get cart item count.
    Note: This app doesn't have a shopping cart feature.
    This endpoint exists to prevent 404 errors from client-side calls.
    """
    return jsonify({
        'count': 0,
        'items': []
    })


@api.route('/v1/convert', methods=['POST'])
def convert():
    """API endpoint for conversion (future)."""
    return jsonify({
        'error': 'API not yet implemented'
    }), 501
