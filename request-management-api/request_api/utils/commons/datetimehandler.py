
from os import stat
from re import VERBOSE
import json
from datetime import datetime as datetime2
from datetime import datetime, timedelta
import holidays
import maya
import os
from dateutil.parser import parse
from pytz import timezone

class datetimehandler:
    """ Supports common date operations

    """
    def gettoday(self,format=None):
        now_pst = maya.parse(maya.now()).datetime(to_timezone=self.getdefaulttimezone(), naive=False)
        return self.__formatdate(now_pst, format)

    def now(self):
        return maya.parse(maya.now()).datetime(to_timezone=self.getdefaulttimezone(), naive=False)
    
    def formatdate(self, input, format=None):
        _inpdate =  self.getdate(input)
        return self.__formatdate(_inpdate, format) 

    def convert_to_pst(self, input, format=None):
        now_pst = maya.parse(self.getdate(input)).datetime(to_timezone=self.getdefaulttimezone(), naive=False)
        return self.__formatdate(now_pst, format) 

    def __formatdate(self, _inpdate, format):
        _format = format if format not in (None, '') else self.getdefaultdateformat()
        return _inpdate.strftime(_format)

    def getdate(self, inputdate):
        return  datetime.strptime(inputdate, "%Y-%m-%d") if isinstance(inputdate, str) else inputdate            
   
    def getdefaulttimezone(self):
        return 'America/Vancouver'

    def getdefaultdateformat(self):
        return '%Y-%m-%d'
