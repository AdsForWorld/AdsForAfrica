import re
import secrets
import time
import logging
import requests
from io import BytesIO
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from PIL import Image

from .. import db, logger, limiter, keys, startat
from ..models import Ad, User
from ..utils import dateunix
import reqmod.imagehandler as ih

bp = Blueprint('api', __name__)

@bp.route('/register/ad', methods=['POST'])
def register():
    """Backend: Register an AD for review"""
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
        friendlyname = str(request.json.get('friendlyname'))
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
        
        file_size = int(response.headers.get('Content-Length', 0))
        if file_size > file_size_limit:
            ad = Ad(title=title, image_url="", clickthrough_url=clickthrough_url, 
                   impressions=0, clicks=0, ts=dateunix(), tags=tags, 
                   campaignid=campaignid, iheight=0, iwidth=0, displays=dispcnt, 
                   reviewed=False)
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
        
        temp_file = BytesIO()
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

        temp_file.seek(0)
        ih.suploadfile(client, temp_file, 'ad-images', f'{adid}/{friendlyname}')
        upurl = f"https://adsforafrica.sfo3.cdn.digitaloceanspaces.com/ad-images/{adid}/{friendlyname}"
        
    else:
        return jsonify({'error': 'File not found'}), 404
    
    ad = Ad(title=title, image_url=upurl, clickthrough_url=clickthrough_url, 
           impressions=0, clicks=0, ts=dateunix(), tags=tags, 
           campaignid=campaignid, iheight=height, iwidth=width, 
           displays=dispcnt, createdby=creator, 
           createdip=request.remote_addr, reviewed=False)
    db.session.add(ad)
    db.session.commit()

    return jsonify({"message": f"Ad registered for review! (about 1-2 business hours PST.)", 
                   "Private Key": "", "adid": ad.id})

@bp.route('/getallads')
def getallads():
    """Debug/Backend function to view all ads + data"""
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

@bp.route('/uptime')
def suptime():
    """[BACKEND FUNCTION] Returns the uptime of the server"""
    return jsonify({'uptime': time.time() - startat})

@bp.route('/accessleasekey', methods=['POST'])
def leasekey():
    """Backend: leases a key for a user to securely submit a form"""
    key = secrets.token_urlsafe(16)
    unixtime = dateunix()
    keys[key] = unixtime + 86400  # 24 hours
    return jsonify({'key': key}), 200
