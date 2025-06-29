import time
import datetime

def dateunix():
    """Returns the current date in unix format"""
    presentDate = datetime.datetime.now()
    return time.mktime(presentDate.timetuple())
