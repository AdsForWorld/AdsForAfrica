import logging
import time
import datetime
import re
import secrets
import threading
import uuid
from io import BytesIO
from urllib.parse import quote_plus

# Flask and related packages
from flask import (
    Flask, request, jsonify, render_template, 
    redirect, url_for, abort, send_from_directory,
    make_response
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# SQLAlchemy components
from sqlalchemy import func
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects import postgresql

# Password handling
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Image processing
from PIL import Image
import requests

# Custom modules
import reqmod.imagehandler as ih  # proprietary file
import reqmod.emailer as email    # proprietary file

#logger
class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.timestamp = int(time.time())
        return super().format(record)


logger = logging.getLogger('adsforafrica')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f'reqmod/logging_storage/access_{datetime.date.today().strftime('%m-%d-%Y')}.log')
file_handler.setFormatter(CustomFormatter('[%(levelname)s][%(timestamp)d]: %(message)s'))
logger.addHandler(file_handler)
#define variables
app = Flask(__name__)
todelete = [] 
keys = {} #userkeys
adminkeys = {} #adminkeys
userkeys = {}
keyadmins = {} #keys to admin plaintextname
validform = [] #valid forms
unauthendpoint = []
betaaccess = []
startat = time.time()
ph = PasswordHasher()
try:
    ecreds = email.credentials()
except:
    logging.log(logging.WARN, "Error in emailer.py, please check the credentials")
    ecreds = None

login_manager = LoginManager()
login_manager.init_app(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

db_pwd = quote_plus('@ghastmuffin!1')
# Replace the PostgreSQL connection strings with SQL Server connection strings

# SQL Server connection settings
server = 'adsforafrica-server.database.windows.net'
port = '1433'
database = 'ads'
users_database = 'userstorage'
username = 'adsforafrica-server-admin'
password = '@ghastmuffin!1'  # Your actual password

# Create the connection strings
connection_string = f"mssql+pyodbc://{username}:{quote_plus(password)}@{server}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
users_connection_string = f"mssql+pyodbc://{username}:{quote_plus(password)}@{server}:{port}/{users_database}?driver=ODBC+Driver+17+for+SQL+Server"

app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_BINDS'] = {
    'users': users_connection_string
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 3600
}



# Additional configuration options
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'connect_args': {
        'Encrypt': 'yes',
        'TrustServerCertificate': 'no',
        'ConnectionTimeout': 30
    }
}

db = SQLAlchemy(app)

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    image_url = db.Column(db.String(300))
    clickthrough_url = db.Column(db.String(300))
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    displays = db.Column(db.Integer, default=1000)
    ts = db.Column(db.Integer)
    tags = db.Column(db.String(100))
    campaignid = db.Column(db.Integer)
    iheight = db.Column(db.Integer)
    iwidth = db.Column(db.Integer)
    contact = db.Column(db.String(200))
    createdby = db.Column(db.String(50))
    authorizer = db.Column(db.String(200))
    reviewed = db.Column(db.Boolean, default=False)

class User(db.Model):
    __bind_key__ = 'users'
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    uuid = db.Column(db.String(1000), unique=True, nullable=False)
    apikey = db.Column(db.String(200), unique=True)
    isadmin = db.Column(db.Boolean, default=False)
    campaignid = db.Column(db.Integer)
    hashpwd = db.Column(db.String(200))
    strikes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.datetime.now)
    email = db.Column(db.String(255), unique=True)  # Ensure email is unique
    emailverified = db.Column(db.Boolean, default=False)
    roles = db.Column(postgresql.ENUM('advertiser', 'Implementer', 'Volunteer', 'Developer', name='user_role'), nullable=False)




# Remove or comment out the SQL Server connection test function
# def test_db_connection():
#     ...
# Call this function when starting your app
# test_db_connection()

#before request
@app.before_request
def filter_invalid_requests():
    if request.method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']:
        app.logger.warning(f"Invalid HTTP method: {request.method} from IP: {request.remote_addr}")
        abort(400)
    if not request.environ.get('SERVER_PROTOCOL').startswith('HTTP/1.') and not request.environ.get('SERVER_PROTOCOL').startswith('HTTP/2'):
        app.logger.warning(f"Invalid HTTP version: {request.environ.get('SERVER_PROTOCOL')} from IP: {request.remote_addr}")
        abort(400)


@app.before_request
def log_request_info():
    global ip
    ip = request.remote_addr
if False:
    #restrict endpoint access
    @app.before_request
    def authenticate():
        global unauthendpoint
        if unauthendpoint is None:
            unauthendpoint = [url_for("index"), url_for('login'), url_for("devlogs")]
        print("authenticating: ", request.url)
        if request.cookies.get('accesskey') is not None and request.cookies.get('accesskey') not in keys and request.url not in unauthendpoint:
            print("unauthenticated user.")
            return "You are not authorized to access this page. Please login to access this page."


#endpoints
@app.route('/', methods=['GET'])
def index():
    """
    Serves the main page of the website
    """
    return render_template('index.html')

@app.route('/robots.txt', methods=['GET'])
def robots():
    """
    Serves the robots.txt file
    """
    return send_from_directory(app.static_folder, 'robots.txt')


@app.route('/devlog', methods=['GET'])
def devlog():
    """
    Serves the development logs page
    """
    return render_template('devlogs.html')


@app.route('/about', methods=['GET'])
def about():
    """
    Serves the about page
    """
    return render_template('abt.html')


@app.route('/click/<adid>', methods=['GET']) 
def click(adid):
    """
    This function records a click on an ad
    """
    ad = Ad.query.filter_by(id=adid).first()
    if ad is None:
        logger.log(logging.WARN, f'[{dateunix()}]: AD NOT FOUND {adid} requested by {ip}')
        return jsonify({'error': 'Ad not found'}), 404

    ad.clicks += 1
    db.session.commit()
    return redirect(ad.clickthrough_url)


@app.route('/show/<adid>/', methods=['GET'])
@limiter.limit("1000 per hour")
def dispad(adid):
    """displays an ad by dynamically generating an html page
    Args:
        adid (int): The id of the ad to display
        viewport (str): The viewport size
    Returns:
        The HTML page, prerendered with the ad
    """
    ad = Ad.query.filter_by(id=adid).first()
    #build more serve logic based off of ad tags
    if ad is None:
        return render_template('notfound.html')
    checkadvalid(adid)
    logger.log(logging.INFO, f'[{dateunix()}]: AD {adid} requested by {ip}')
    ad.impressions += 1
    db.session.commit()
    return render_template('viewad.html', adid=ad.id, adalt=ad.title, adurl=ad.image_url, adlink=url_for('click', adid=ad.id))


@app.route('/reviewer/adreview', methods=['GET'])
def adreview():
    if request.cookies.get('accesskey') is None or request.cookies.get('accesskey') not in adminkeys:
        return redirect(url_for('login'))
    ad = Ad.query.filter_by(reviewed=False).first()
    access = request.cookies.get('accesskey')
    if ad is None:
        return "There are currently no ads to review. You have been moved to a different portal."
    if access == None:
        return redirect(url_for('login'))
    if access not in adminkeys:
        return "You do not have access to this page. Please login to access this page."
    elif adminkeys[access] < dateunix():
        return f"Your access key has expired. Please login to access this page. <a href='{url_for('login')}'>click here to redirect</a>"
    else:
        return render_template('adview/index.html', modname=keyadmins[request.cookies.get('accesskey')], title=ad.title, image_url=ad.image_url, clickthrough_url=ad.clickthrough_url, impressions=ad.impressions, clicks=ad.clicks, ts=ad.ts, tags=ad.tags, campaignid=ad.campaignid, iheight=ad.iheight, iwidth=ad.iwidth, displays=ad.displays, createdby=ad.createdby, createdip=ad.createdip, adid=ad.id)
    

@app.route('/login')
def login():
    formkey = secrets.token_urlsafe(5)
    validform.append(formkey)
    logging.log(logging.INFO, f'[{dateunix()}]: Form key generated: {formkey}')
    return render_template('login.html', validformid=formkey)
    #the function you're probably looking for is chkcreds() in the backend


@app.route('/`registerad`', methods=['GET'])
def registerfrnt():
    """frontend of registering a ad
    """
    accesskey = request.cookies.get('accesskey')
    if accesskey is None or accesskey not in userkeys or accesskey not in adminkeys:
        return redirect(url_for('login'))
    if userkeys[accesskey]['expiry'] < dateunix():
        userkeys.pop(accesskey)
        return redirect(url_for('login'))
    
    userkeys[request.cookies.get('accesskey')]
    formkey = secrets.token_urlsafe(5)
    validform.append(formkey)
    return render_template('register_ad.html', username=userkeys[accesskey]['username'], validformid=formkey)


@app.route('/signup', methods=['GET'])
def signup():
    """Serve the signup.html webpage. Validate form"""
    formkey = secrets.token_urlsafe(5)
    validform.append(formkey)
    return render_template('signup.html', validformid=formkey)


@app.route('/volunteer')
def volunteer():
    return "Volunteering page is currently unavaliable. Please check back later."


@app.route('/apply', methods=['GET'])
def apply():
    return "Apply page is currently unavaliable. Please check back later. Avaliable positions: volunteer (moderator, developer, coordinator), serverless hosting (using your computer to power SOME of our compute capabilities.)"


@app.route('/emailverify/<id>', methods=['GET'])
def verifyemail(id):
    """
    verifies a user's email
    """
    user = User.query.filter_by(id=id).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    user.emailverified = True
    db.session.commit()
    return "Email Verified! Please await manual approval. You will recieve an email when your account is approved."


#backend endpoints
@app.route('/backend/register/ad/', methods=['POST'])
def register():
    """
    Backend: Register an AD for reivew
    Args:
        title: str (title of ad, if image cannot be shown)
        image_url: str (url)
        clickthrough_url: str (url)
        tags: str (split via ,)
        displays: int (alloted displays)
        campaignid: int (campaign id)
    Returns: 
        JSON Response
    """
    title = request.json.get('title')
    image_url = request.json.get('image_url')
    clickthrough_url = request.json.get('clickthrough_url')
    campaignid = request.json.get('campaignid')
    contactemail = request.json.get('contact')
    tags = request.json.get('tags')
    dispcnt = request.json.get('displays')

    user = User.query.filter_by(email=contactemail).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    else:
        creator = user.username
    if user.strikes >= 3:
        return jsonify({'error': 'User has too many strikes'}), 403


    if title is None or image_url is None or clickthrough_url is None or campaignid:
        return jsonify({'error': 'Missing data'}), 400
    try:
        friendlyname = str(request.json.get('friendlyname')) #in future will be randomized
    except:
        friendlyname = 'default'
    adid = db.session.query(func.count(Ad.id)).scalar()


    print(title, image_url, clickthrough_url)
    client = ih.startsession()
    response = requests.get(image_url, stream=True)

    if response.status_code == 200:

        file_size_limit = 15 * 1024 * 1024  # 15MB
        total_size = 0
        chunk_size = 1024  # 1KB
        #basic checks
        file_size = int(response.headers.get('Content-Length', 0))
        if file_size > file_size_limit:
            ad = Ad(title=title, image_url="", clickthrough_url=clickthrough_url, impressions=0, clicks=0, ts=dateunix(), tags=tags, campaignid=campaignid, iheight=0, iwidth=0, displays=dispcnt, reviewed=False)
            db.session.add(ad)
            db.session.commit()
            return jsonify({'warn': 'File size exceeds the limit, we will still host your ad, however your image is set to: hosted by you. Review Submission Success!'}), 507
        if friendlyname == 'default':
            content_disposition = response.headers.get('Content-Disposition')
            if content_disposition:
                filename = re.findall('filename="(.+)"', content_disposition)
                if filename:
                    friendlyname = filename[0]
                else:
                    friendlyname = 'default_filename'
            else:
                friendlyname = 'default_filename'
        # Create a temporary file-like object in memory
        from io import BytesIO
        temp_file = BytesIO()
        # Extract filename from Content-Disposition header
        try:
            img = Image.open(temp_file)
            width, height = img.size
        except:
            width, height = 0, 0
        for chunk in response.iter_content(chunk_size=chunk_size):
            total_size += len(chunk)
            if total_size > file_size_limit:
                logger.log(logging.CRITICAL, f'[{dateunix()}, FAILSAFE_ERROR]: FILESIZE MAX REACHED, !!{image_url}!!\n')
                return jsonify({'error': 'File size exceeds the limit'}), 400
            temp_file.write(chunk)

        temp_file.seek(0)  # Reset the file pointer to the beginning
        # Upload the image to the CDN
        ih.suploadfile(client, temp_file, 'ad-images', f'{adid}/{friendlyname}')
        upurl = f"https://adsforafrica.sfo3.cdn.digitaloceanspaces.com/ad-images/{adid}/{friendlyname}"
        
    else:
        return jsonify({'error': 'File not found'}), 404
    ad = Ad(title=title, image_url=upurl, clickthrough_url=clickthrough_url, impressions=0, clicks=0, ts=dateunix(), tags=tags, campaignid=campaignid, iheight=height, iwidth=width, displays=dispcnt, createdby=creator, createdip=ip, reviewed=False)
    db.session.add(ad)
    db.session.commit()

    return jsonify({"message": f"Ad registered for review! (about 1-2 buisness hours PST.)", "Private Key": "", "adid": ad.id})

@app.route('/datares')
def datares():
    return "Data residency: US-WEST-2 (Los Angeles, datacenter-xact: LA HABRA, CALIFORNIA). This page is served by Korea, Republic of: Central. (Seoul, servr-xact: CHUNCHEON, ROK). (str: POSTGRES=LA-FLASKNGINXPROXY=T,)", 302
@app.route('/backend/credentialschk', methods=['POST'])
@limiter.limit("30 per minute")
def chkcreds():
    """
    Backend: Checks if the credentials are valid (currently only moderators accessing review endpoint.)
    """
    username = request.form.get('username')
    password = request.form.get('password')
    validchk = request.form.get('valid') #non user assigned

    if validchk not in validform:
        print(validchk, validform)
        return f"Your form is incorrectly signed, or the signature has expired.", 500
    
    validform.remove(validchk)

    user = User.query.filter_by(username=username).first()
    if user is None:
        return f"User is Nonetype. Click here to retry. <a href='{url_for('login')}'>click here to redirect</a> OR signup <a href='{url_for('signup')}'>here</a>"
    else:
        try:
            ph.verify(user.hashpwd, password)
        except VerifyMismatchError:
            return f"login failed, invalid credentials. Click here to retry.<a href='{url_for('login')}'>click here to redirect</a>"
        if username == user.username:
            if ph.check_needs_rehash(user.hashpwd):
                user.hashpwd = ph.hash(password)
                db.session.commit()
            isadmin = user.isadmin
            if isadmin:
                response = make_response(redirect(url_for('adreview')))
                key = secrets.token_urlsafe(16)  # Generate a secure key, TODO: for later make a private and public keypair
                adminkeys[key] = dateunix() + 86400  # Set key to expire in 24 hours\
                keyadmins[key] = username
                response.set_cookie('accesskey', key, max_age=86400)  # Set cookie for 24 hours
                return response
            else:
                response = make_response(redirect(url_for('index')))
                key = secrets.token_urlsafe(8)  # Generate a secure key, TODO: for later make a private and public keypair
                response.set_cookie('accesskey', key, max_age=86400)
                userkeys[key] = {
                    'expiry': dateunix() + 86400,  # Set key to expire in 24 hours
                    'username': username
                }
                return response
        else:
            return f"login failed, invalid credentials. Click here to retry.<a href='{url_for('login')}'>click here to redirect</a>"
@app.route('/backend/register/admin/', methods=['POST'])
def createadmin():
    """
    Backend: Creates a new admin
    USAGE: This endpoint should be a BACKEND endpoint that a officiator uses to CREATE, not APPLY admin status to an account
    """
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    v_username = request.form.get('v_username')
    v_password = request.form.get('v_password')
    v_key = request.form.get('key')
    if create_admin_account(username, password, email, v_username, v_password, v_key) == 200:
        return 200
    else:
        return 400

@app.route('/backend/register/user/', methods=['POST'])
def createuser():
    """
    Backend: Creates a new (unverified) user NON ADMIN, see the BACKEND endpoint above to create an admin
    """
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
    
    user = User(username=username, hashpwd=ph.hash(password), email=email, isadmin=False, roles=role, uuid=str(uuid.uuid4()))
    
    
    db.session.add(user)
    db.session.commit()
    return "request completed successfully", 200



@app.route('/getallads', methods=['GET'])
def getallads():
    """
    Debug/Backend function to view all ads + data
    """
    ads = Ad.query.all()
    ads_list = []
    for ad in ads:
        ads_list.append({
            'id': ad.id,
            'title': ad.title,
            'image_url': ad.image_url,
            'clickthrough_url': ad.clickthrough_url,
            'impressions': ad.impressions,
            'clicks': ad.clicks,
            'timestampcreated': ad.ts,
            'tags': ad.tags,
            'displays': ad.displays,
            'campaignid': ad.campaignid,
            'height': ad.iheight,
            'width': ad.iwidth,
            'contact': ad.contact,
            'createdby': ad.createdby,
            'createdip': ad.authorizer
        })
    return jsonify(ads_list)


@app.route('/uptime/', methods=['GET'])
def suptime():
    """
    [BACKEND FUNCTION] Returns the uptime of the server
    """
    return jsonify({'uptime': time.time() - startat})


@app.route('/impressions/<ad>', methods=['POST', 'GET'])
def showimpressions(ad):
    """
    [BACKEND FUNCTION] Returns Ad Impressions (time since creation)
    """
    ad = Ad.query.filter_by(title=ad).first()
    if ad is None:
        return jsonify({'error': 'Ad not found'}), 404
    return jsonify({'impressions': ad.impressions})


@app.route('/accessleasekey', methods=['POST'])
def leasekey():
    """Backend: leases a key for a user to securely submit a form"""
    key = secrets.token_urlsafe(16)
    unixtime = dateunix()
    #key and expiry time
    keys[key] = unixtime + 86400 #24 hours
    return jsonify({'key': key}), 200


#backend functions
def create_admin_account(c_username, c_password, email, v_username, v_password, v_key):
    """
    Creates an admin account with the given username, password, and email.
    """
    # Check if the user already exists
    """
    c_username = request.form.get('username') #username of user to create
    c_password = request.form.get('password') #password of user to create
    v_username = request.form.get('v_username') #username of officiator (verifier_username)
    v_password = request.form.get('v_password') #password of officiator (verifier_password)
    v_key = request.form.get('key') #adminkey given to admin every 24 hours upon reverification (user should not directly have access to this.)
    validchk = request.form.get('valid') #automatically assigned valid key, should be passed by calling function
    """
    if User.query.filter_by(username=c_username).first() is not None:
        logger.info(f"Admin account creation failed: Username '{c_username}' already exists")
        return 400 #account exists
    if v_username is None or v_password is None or v_key is None:
        return 400 #missing data
    
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
    # Hash the password
    hashed_password = ph.hash(c_password)

    # Create the admin user
    admin_user = User(
        username=c_username,
        hashpwd=hashed_password,
        email=email,
        isadmin=True,
        uuid=str(uuid.uuid4())
    )

    # Add the admin user to the database
    db.session.add(admin_user)
    db.session.commit()

    logger.info(f"Admin account created successfully: Username '{c_username}', officiator: '{v_username}'")
    return 200 #success!


def migratead(id, authorizer):
    """migrates an ad from the review database to the main database"""
    ad = Ad.query.filter_by(id=id).first()
    if ad is None:
        return
    ad.reviewed = True
    db.session.commit()
    return


def checkadvalid(adid):
    ad = Ad.query.filter_by(id=adid).first()
    displays = int(ad.displays)
    if ad is None:
        return False
    curdisp = (ad.impressions * 0.5 + ad.clicks)
    print(curdisp, displays)
    if curdisp >= displays:
        with open("messages/successad.txt", "r") as f:
            body = f.read()
        if ecreds is not None:
            email.sendemail(ecreds, "Campaign/Ad Finished!", body=body, sendto="aghastmuffin@gmail.com", issuer="AdsForAfrica", reqby="System", reason="Ad Campaign Finished", sendfrom="adsforworld+adsforafrica_auto@gmail.com") 
        print("Deletion Scheduled for ad: ", adid)
        todelete.append(adid)
        delete_ad()
        return False
    return True

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def delete_ad():
    if len(todelete) == 0:
        print("No queued deletions")
        return
    for adid in todelete:
        ad = Ad.query.filter_by(id=adid).first()
        db.session.delete(ad)
        print("Deleted ad: ", adid)
    db.session.commit()
    logger.log(logging.INFO, f'[{dateunix()}]: Deleted ad: {adid}')
    return


def dateunix():
    """
    Returns the current date in unix format
    """
    presentDate = datetime.datetime.now()
    return time.mktime(presentDate.timetuple())

if __name__ == '__main__':

    with app.app_context():
        db.create_all()
    logger.log(logging.INFO, f'[{dateunix()}]: Server started')
    app.run(debug=True)
