import jinja2
from request_api.services.notifications.duecalculator import duecalculator
from datetime import datetime

def formatdate(value, format):    
    return duecalculator().formatedate(value, format)

def init_filters():
    jinja2.filters.FILTERS['formatdate'] = formatdate

        