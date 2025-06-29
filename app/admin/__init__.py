import secrets
import logging
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from argon2.exceptions import VerifyMismatchError
from .. import db, logger, ph, adminkeys, keyadmins, userkeys, validform
from ..models import Ad, User
from ..utils import dateunix

bp = Blueprint('admin', __name__)

@bp.route('/adreview')
def adreview():
    """Admin ad review interface"""
    if request.cookies.get('accesskey') is None or request.cookies.get('accesskey') not in adminkeys:
        return redirect(url_for('auth.login'))
    
    ad = Ad.query.filter_by(reviewed=False).first()
    access = request.cookies.get('accesskey')
    
    if ad is None:
        return "There are currently no ads to review. You have been moved to a different portal."
    
    if access == None:
        return redirect(url_for('auth.login'))
    
    if access not in adminkeys:
        return "You do not have access to this page. Please login to access this page."
    elif adminkeys[access] < dateunix():
        return f"Your access key has expired. Please login to access this page. <a href='{url_for('auth.login')}'>click here to redirect</a>"
    else:
        return render_template('adview/index.html', 
                             modname=keyadmins[request.cookies.get('accesskey')], 
                             title=ad.title, 
                             image_url=ad.image_url, 
                             clickthrough_url=ad.clickthrough_url, 
                             impressions=ad.impressions, 
                             clicks=ad.clicks, 
                             ts=ad.ts, 
                             tags=ad.tags, 
                             campaignid=ad.campaignid, 
                             iheight=ad.iheight, 
                             iwidth=ad.iwidth, 
                             displays=ad.displays, 
                             createdby=ad.createdby, 
                             adid=ad.id)

@bp.route('/registerad')
def registerfrnt():
    """Frontend of registering an ad"""
    accesskey = request.cookies.get('accesskey')
    if accesskey is None or accesskey not in userkeys or accesskey not in adminkeys:
        return redirect(url_for('auth.login'))
    if userkeys[accesskey]['expiry'] < dateunix():
        userkeys.pop(accesskey)
        return redirect(url_for('auth.login'))
    
    formkey = secrets.token_urlsafe(5)
    validform.append(formkey)
    return render_template('register_ad.html', 
                         username=userkeys[accesskey]['username'], 
                         validformid=formkey)

@bp.route('/register/admin', methods=['POST'])
def createadmin():
    """Backend: Creates a new admin"""
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    v_username = request.form.get('v_username')
    v_password = request.form.get('v_password')
    v_key = request.form.get('key')
    
    if create_admin_account(username, password, email, v_username, v_password, v_key) == 200:
        return "Admin created successfully", 200
    else:
        return "Failed to create admin", 400

def create_admin_account(c_username, c_password, email, v_username, v_password, v_key):
    """Creates an admin account with the given username, password, and email."""
    if User.query.filter_by(username=c_username).first() is not None:
        logger.info(f"Admin account creation failed: Username '{c_username}' already exists")
        return 400
    
    if v_username is None or v_password is None or v_key is None:
        return 400
    
    try:
        admin = User.query.filter_by(username=v_username).first()
        if admin.isadmin and admin is not None:
            if v_key in adminkeys and adminkeys[v_key] > dateunix():
                try:
                    ph.verify(admin.hashpwd, v_password)
                except VerifyMismatchError:
                    return 400
    except:
        logger.log(logging.ERROR, f"Admin account creation failed: Error while verifying admin password for '{v_username}'")
        return 400
    
    hashed_password = ph.hash(c_password)
    
    admin_user = User(
        username=c_username,
        hashpwd=hashed_password,
        email=email,
        isadmin=True,
        uuid=str(uuid.uuid4())
    )
    
    db.session.add(admin_user)
    db.session.commit()
    
    logger.info(f"Admin account created successfully: Username '{c_username}', officiator: '{v_username}'")
    return 200

def migratead(id, authorizer):
    """migrates an ad from the review database to the main database"""
    ad = Ad.query.filter_by(id=id).first()
    if ad is None:
        return
    ad.reviewed = True
    db.session.commit()
    return
