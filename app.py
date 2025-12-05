# app.py
"""Application entry point."""

import os
from app import create_app
from app.extensions import db
from app.models import Account, Conversion, CreditsTransaction, Order, Package

# Create Flask app
app = create_app(os.getenv('FLASK_ENV') or 'development')


@app.shell_context_processor
def make_shell_context():
    """Make shell context with database and models."""
    return {
        'db': db,
        'Account': Account,
        'Conversion': Conversion,
        'CreditsTransaction': CreditsTransaction,
        'Order': Order,
        'Package': Package
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
