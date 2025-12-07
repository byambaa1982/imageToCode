# app/api/routes.py
"""API routes (future implementation)."""

from flask import jsonify
from app.api import api


@api.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })


@api.route('/v1/convert', methods=['POST'])
def convert():
    """API endpoint for conversion (future)."""
    return jsonify({
        'error': 'API not yet implemented'
    }), 501
