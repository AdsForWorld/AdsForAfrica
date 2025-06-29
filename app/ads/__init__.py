import logging
from flask import Blueprint, request, jsonify, redirect, render_template, url_for
from app import db, logger, limiter, todelete
from app.models import Ad
from app.utils import dateunix

bp = Blueprint('ads', __name__)

@bp.route('/click/<adid>')
def click(adid):
    """This function records a click on an ad"""
    ad = Ad.query.filter_by(id=adid).first()
    if ad is None:
        logger.log(logging.WARN, f'[{dateunix()}]: AD NOT FOUND {adid} requested by {request.remote_addr}')
        return jsonify({'error': 'Ad not found'}), 404

    ad.clicks += 1
    db.session.commit()
    return redirect(ad.clickthrough_url)

@bp.route('/show/<adid>/')
@limiter.limit("1000 per hour")
def dispad(adid):
    """displays an ad by dynamically generating an html page
    Args:
        adid (int): The id of the ad to display
    Returns:
        The HTML page, prerendered with the ad
    """
    ad = Ad.query.filter_by(id=adid).first()
    if ad is None:
        return render_template('notfound.html')
    
    checkadvalid(adid)
    logger.log(logging.INFO, f'[{dateunix()}]: AD {adid} requested by {request.remote_addr}')
    ad.impressions += 1
    db.session.commit()
    return render_template('viewad.html', 
                         adid=ad.id, 
                         adalt=ad.title, 
                         adurl=ad.image_url, 
                         adlink=url_for('ads.click', adid=ad.id))

@bp.route('/impressions/<ad>', methods=['POST', 'GET'])
def showimpressions(ad):
    """[BACKEND FUNCTION] Returns Ad Impressions (time since creation)"""
    ad = Ad.query.filter_by(title=ad).first()
    if ad is None:
        return jsonify({'error': 'Ad not found'}), 404
    return jsonify({'impressions': ad.impressions})

def checkadvalid(adid):
    """Check if an ad is still valid based on display limits"""
    ad = Ad.query.filter_by(id=adid).first()
    displays = int(ad.displays)
    if ad is None:
        return False
    curdisp = (ad.impressions * 0.5 + ad.clicks)
    print(curdisp, displays)
    if curdisp >= displays:
        # Import here to avoid circular imports
        import reqmod.emailer as email
        from app import ecreds
        
        with open("messages/successad.txt", "r") as f:
            body = f.read()
        if ecreds is not None:
            email.sendemail(ecreds, "Campaign/Ad Finished!", body=body, 
                          sendto="aghastmuffin@gmail.com", issuer="AdsForAfrica", 
                          reqby="System", reason="Ad Campaign Finished", 
                          sendfrom="adsforworld+adsforafrica_auto@gmail.com") 
        print("Deletion Scheduled for ad: ", adid)
        todelete.append(adid)
        delete_ad()
        return False
    return True

def delete_ad():
    """Delete ads that are scheduled for deletion"""
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
