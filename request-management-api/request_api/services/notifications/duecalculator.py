
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

class duecalculator:
    """ Due date calculator helper service

    """
                
    def getpreviousbusinessday(self, cfrduedate,ca_holidays):
        _prevbusinessday = self.__getpreviousweekday(cfrduedate)
        if self.__isholiday(_prevbusinessday,ca_holidays) == False:            
            return _prevbusinessday
        else:
            return self.getpreviousbusinessday(_prevbusinessday,ca_holidays)
 
    def gettoday(self):
        now_pst = maya.parse(maya.now()).datetime(to_timezone=self.__getdefaulttimezone(), naive=False)
        return now_pst.strftime(self.__getdefaultdateformat()) 
    
    def formatduedate(self,input):
        _inpdate = datetime.strptime(input, "%Y-%m-%d") if isinstance(input, str) else input   
        return _inpdate.strftime(self.__getdefaultdateformat())
    
    def getholidays(self):        
        ca_holidays = []
        for date, name in sorted(holidays.CA(prov='BC', years=datetime.today().year).items()):
            ca_holidays.append(date.strftime(self.__getdefaultdateformat()))
        if 'FOI_ADDITIONAL_HOLIDAYS' in os.environ and os.getenv('FOI_ADDITIONAL_HOLIDAYS') != '':
            _addldays = os.getenv('FOI_ADDITIONAL_HOLIDAYS')
            for _addlday in _addldays.split(","):
                ca_holidays.append(_addlday.strip().replace('XXXX',str(datetime.today().year)))
        return ca_holidays    
        
    def __getpreviousweekday(self, cfrduedate):
        diff = 1
        _cfrduedate = datetime.strptime(cfrduedate, "%Y-%m-%d") if isinstance(cfrduedate, str) else cfrduedate   
        if _cfrduedate.weekday() == 0:
            diff = 3
        elif _cfrduedate.weekday() == 6:
            diff = 2
        else :
            diff = 1  
        res = _cfrduedate - timedelta(days=diff)
        return res.strftime(self.__getdefaultdateformat())            
   
    def __isholiday(self, input, ca_holidays):
        return input in ca_holidays   
      
    def __getdefaulttimezone(self):
        return 'America/Vancouver'

    def __getdefaultdateformat(self):
        return '%Y-%m-%d'
