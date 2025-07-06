#!/usr/bin/env python3
"""
Refactored AdsForAfrica Flask Application using Blueprint Architecture
This replaces the monolithic app.py with a modular blueprint-based structure
"""

from app import create_app, db
import reqmod.emailer as email
import logging

_VERSION = "1.0.1"
_SOURCE = "GITHUB"
_SIGN = "LEVI-TAESON-KIM-BROWN-AFA-SAN-FRANCISCO"
_SIGNDATE = "2025-07-06"
_SERVER = "CHUNCHEON-SEOUL" #intended recipient. Usage on other servers is restricted

# Try to initialize email credentials
try:
    ecreds = email.credentials()
except:
    logging.log(logging.WARN, "Error in emailer.py, please check the credentials")
    ecreds = None

# Create the Flask application using the application factory pattern
app = create_app()

# Make ecreds available globally for the application
app.config['EMAIL_CREDENTIALS'] = ecreds

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    from app.models import User, Ad
    return {'db': db, 'User': User, 'Ad': Ad}

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Log server startup
        from app import logger
        from app.utils import dateunix
        logger.log(logging.INFO, f'[{dateunix()}]: Server started with blueprint architecture')
        
    # Run the application
    app.run(debug=True)
