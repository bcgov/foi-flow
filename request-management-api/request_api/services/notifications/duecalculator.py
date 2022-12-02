
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

    def formatduedate(self,input):
        return self.__formatdate(input)

    def addbusinessdays(self, inpdate, days):
        _holidays = self.getholidays()
        businessdays = 0
        __calcdate = self.__getdate(inpdate)
        while businessdays < days:
            __calcdate =  __calcdate + timedelta(days=1)
            if self.__formatdate(__calcdate) not in _holidays and self.__isweekday(__calcdate) == True:
                businessdays += 1              
        return __calcdate

    def getbusinessdaysbetween(self, date1, date2=None):
        _holidays = self.getholidays()
        businessdays = 0
        date2 = date2 if date2 not in (None, '') else self.gettoday()
        __fromdate = self.__getdate(date1) if self.__getdate(date1).date() <= self.__getdate(date2).date() else self.__getdate(date2)
        __todate = self.__getdate(date2) if self.__getdate(date2).date() >= self.__getdate(date1).date() else self.__getdate(date1)
        __calcdate =__fromdate
        while self.__getdate(__calcdate).date() <= self.__getdate(__todate).date():
            __calcdate =  __calcdate + timedelta(days=1)
            if self.__formatdate(__calcdate) not in _holidays and self.__isweekday(__calcdate) == True:
                businessdays += 1
        return businessdays    

 
    def gettoday(self):
        now_pst = maya.parse(maya.now()).datetime(to_timezone=self.__getdefaulttimezone(), naive=False)
        return now_pst.strftime(self.__getdefaultdateformat()) 
    
    def getholidays(self):
        ca_holidays = []
        currentyear = datetime.today().year
        years = [currentyear - 1, currentyear, currentyear + 1] 
        for year in years:
            ca_holidays.extend(self.__getholidaysbyyear(year))
        return ca_holidays


    def __getholidaysbyyear(self, year):        
        ca_holidays = []
        for date, name in sorted(holidays.CA(prov='BC', years=year).items()):
            ca_holidays.append(date.strftime(self.__getdefaultdateformat()))
        if 'FOI_ADDITIONAL_HOLIDAYS' in os.environ and os.getenv('FOI_ADDITIONAL_HOLIDAYS') != '':
            _addldays = os.getenv('FOI_ADDITIONAL_HOLIDAYS')
            for _addlday in _addldays.split(","):
                ca_holidays.append(_addlday.strip().replace('XXXX',str(year)))
        return ca_holidays    

    def __formatdate(self, input):
        _inpdate =  self.__getdate(input)
        return _inpdate.strftime(self.__getdefaultdateformat())   
    
    def __isweekday(self, inpdate):
        _inpdate = self.__getdate(inpdate)
        if _inpdate.weekday() < 5:
            return True
        else:   
            return False 
    
    def __getpreviousweekday(self, cfrduedate):
        diff = 1
        _cfrduedate = self.__getdate(cfrduedate)  
        if _cfrduedate.weekday() == 0:
            diff = 3
        elif _cfrduedate.weekday() == 6:
            diff = 2
        else :
            diff = 1  
        res = _cfrduedate - timedelta(days=diff)
        return res.strftime(self.__getdefaultdateformat())     

    def __getdate(self, inputdate):
        return  datetime.strptime(inputdate, "%Y-%m-%d") if isinstance(inputdate, str) else inputdate            
   
    def __isholiday(self, input, ca_holidays):
        return input in ca_holidays   
      
    def __getdefaulttimezone(self):
        return 'America/Vancouver'

    def __getdefaultdateformat(self):
        return '%Y-%m-%d'
