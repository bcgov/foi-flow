import jinja2
from request_api.utils.commons.datetimehandler import datetimehandler
from datetime import datetime

def formatdate(value, format):    
    return datetimehandler().formatdate(value, format)

def init_filters():
    jinja2.filters.FILTERS['formatdate'] = formatdate

        