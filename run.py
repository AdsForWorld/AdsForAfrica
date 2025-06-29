#!/usr/bin/env python3

from app import create_app, db
import reqmod.emailer as email
import logging

# Try to initialize email credentials
try:
    ecreds = email.credentials()
except:
    logging.log(logging.WARN, "Error in emailer.py, please check the credentials")
    ecreds = None

app = create_app()

# Make ecreds available globally
app.config['EMAIL_CREDENTIALS'] = ecreds

@app.shell_context_processor
def make_shell_context():
    from app.models import User, Ad
    return {'db': db, 'User': User, 'Ad': Ad}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from app import logger
        from app.utils import dateunix
        logger.log(logging.INFO, f'[{dateunix()}]: Server started')
    app.run(debug=True)
