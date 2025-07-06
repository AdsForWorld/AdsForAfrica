from flask import Blueprint, render_template, send_from_directory, current_app

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Serves the main page of the website"""
    return render_template('index.html')

@bp.route('/robots.txt')
def robots():
    """Serves the robots.txt file"""
    return send_from_directory(current_app.static_folder, 'robots.txt')

@bp.route('/devlog')
def devlog():
    """Serves the development logs page"""
    return render_template('devlogs.html')

@bp.route('/about')
def about():
    """Serves the about page"""
    return render_template('abt.html')

@bp.route('/volunteer')
def volunteer():
    return "Volunteering page is currently unavailable. Please check back later."

@bp.route('/ourteam')
def ourteam():
    """Serves the our team page"""
    return render_template('ourteam.html')

@bp.route('/apply')
def apply():
    return "Apply page is currently unavailable. Please check back later. Available positions: volunteer (moderator, developer, coordinator), serverless hosting (using your computer to power SOME of our compute capabilities.)"

@bp.route('/datares')
def datares():
    return "Data residency: US-WEST-2 (Los Angeles, datacenter-xact: LA HABRA, CALIFORNIA). This page is served by Korea, Republic of: Central. (Seoul, servr-xact: CHUNCHEON, ROK). (str: POSTGRES=LA-FLASKNGINXPROXY=T,)", 302
