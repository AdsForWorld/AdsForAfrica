import secrets
import logging
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, make_response, jsonify
from argon2.exceptions import VerifyMismatchError
from .. import ph, logger, adminkeys, userkeys, keyadmins, validform, db, limiter
from ..models import User
from ..utils import dateunix

bp = Blueprint('auth', __name__)

@bp.route('/login')
def login():
    formkey = secrets.token_urlsafe(5)
    validform.append(formkey)
    logging.log(logging.INFO, f'[{dateunix()}]: Form key generated: {formkey}')
    return render_template('login.html', validformid=formkey)

@bp.route('/signup')
def signup():
    """Serve the signup.html webpage. Validate form"""
    formkey = secrets.token_urlsafe(5)
    validform.append(formkey)
    return render_template('signup.html', validformid=formkey)

@bp.route('/emailverify/<id>')
def verifyemail(id):
    """Verifies a user's email"""
    user = User.query.filter_by(id=id).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    user.emailverified = True
    db.session.commit()
    return "Email Verified! Please await manual approval. You will receive an email when your account is approved."

@bp.route('/credentialschk', methods=['POST'])
@limiter.limit("30 per minute")
def chkcreds():
    """Backend: Checks if the credentials are valid"""
    username = request.form.get('username')
    password = request.form.get('password')
    validchk = request.form.get('valid')

    if validchk not in validform:
        print(validchk, validform)
        return f"Your form is incorrectly signed, or the signature has expired.", 500
    
    validform.remove(validchk)

    user = User.query.filter_by(username=username).first()
    if user is None:
        return f"User is Nonetype. Click here to retry. <a href='{url_for('auth.login')}'>click here to redirect</a> OR signup <a href='{url_for('auth.signup')}'>here</a>"
    elif len(user) < 1:
        return f"Woah there buster! You've uncovered a bountiful error. Report this to error@adsforafrica.me for 10$ reward, USERERRORtmu-{len(user)}TooManyUsers;DB=LA-HABRA;SERVEDBY:LOCALE-IDENTIFIER-NOT-PRESENT-PROBABLY-CHUNCHEON-SEOUL.misconfigmisconfig.misconfig.misconfig. fix ts seoul 😭😭"
    else:
        try:
            ph.verify(user.hashpwd, password)
        except VerifyMismatchError:
            return f"login failed, invalid credentials. Click here to retry.<a href='{url_for('auth.login')}'>click here to redirect</a>"
        
        if username == user.username:
            if ph.check_needs_rehash(user.hashpwd):
                user.hashpwd = ph.hash(password)
                db.session.commit()
            
            isadmin = user.isadmin
            if isadmin:
                response = make_response(redirect(url_for('admin.adreview')))
                key = secrets.token_urlsafe(16)
                adminkeys[key] = dateunix() + 86400
                keyadmins[key] = username
                response.set_cookie('accesskey', key, max_age=86400)
                return response
            else:
                response = make_response(redirect(url_for('main.index')))
                key = secrets.token_urlsafe(8)
                response.set_cookie('accesskey', key, max_age=86400)
                userkeys[key] = {
                    'expiry': dateunix() + 86400,
                    'username': username
                }
                return response
        else:
            return f"login failed, invalid credentials. Click here to retry.<a href='{url_for('auth.login')}'>click here to redirect</a>"

@bp.route('/register/user', methods=['POST'])
def createuser():
    """Backend: Creates a new (unverified) user NON ADMIN"""
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    role = request.form.get('reason')

    if username is None or password is None or email is None:
        return jsonify({'error': 'Missing data'}), 400

    if role not in ['advertiser', 'Implementer', 'Volunteer', 'Developer']:
        return jsonify({'error': 'invalid role'}), 400
    
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'Username/User already exists'}), 400
    
    user = User(
        username=username, 
        hashpwd=ph.hash(password), 
        email=email, 
        isadmin=False, 
        roles=role, 
        uuid=str(uuid.uuid4())
    )
    
    db.session.add(user)
    db.session.commit()
    return "request completed successfully", 200
