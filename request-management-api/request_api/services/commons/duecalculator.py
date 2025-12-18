
from os import stat
from re import VERBOSE
from datetime import datetime as datetime2
from datetime import datetime, timedelta
import holidays
import os
from dateutil.parser import parse
from pytz import timezone
from request_api.utils.commons.datetimehandler import datetimehandler

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
        return datetimehandler().formatdate(input)

    def addbusinessdays(self, inpdate, days):
        _holidays = self.getholidays()
        businessdays = 0
        __calcdate = datetimehandler().getdate(inpdate)
        while businessdays < days:
            __calcdate =  __calcdate + timedelta(days=1)
            if self.isbusinessday(__calcdate, _holidays) == True:
                businessdays += 1              
        return __calcdate

    def getbusinessdaysbetween(self, date1, date2=None):
        _holidays = self.getholidays()
        businessdays = 0
        date2 = date2 if date2 not in (None, '') else self.gettoday()
        _date1_date_fmt = datetimehandler().getdate(date1)
        _date2_date_fmt = datetimehandler().getdate(date2)
        __fromdate = _date1_date_fmt if _date1_date_fmt <= _date2_date_fmt else _date2_date_fmt
        __todate = _date2_date_fmt if _date2_date_fmt >= _date1_date_fmt else _date1_date_fmt
        __fromcalcdate =__fromdate
        while datetimehandler().getdate(__fromcalcdate).date() < datetimehandler().getdate(__todate).date():
            if self.isbusinessday(__fromcalcdate, _holidays) == True:
                businessdays += 1
            __fromcalcdate =  __fromcalcdate + timedelta(days=1)           
        return businessdays  

    def getholidays(self):
        ca_holidays = []
        currentyear = datetime.today().year
        years = [currentyear - 1, currentyear, currentyear + 1] 
        for year in years:
            ca_holidays.extend(self.__getholidaysbyyear(year))
        return ca_holidays

    def gettoday(self):
        return datetimehandler().gettoday()

    def now(self):
        return datetimehandler().now()

    def __getholidaysbyyear(self, year):        
        ca_holidays = []
        for date, name in sorted(holidays.CA(prov='BC', years=year).items()):
            ca_holidays.append(date.strftime(datetimehandler().getdefaultdateformat()))
        if 'FOI_ADDITIONAL_HOLIDAYS' in os.environ and os.getenv('FOI_ADDITIONAL_HOLIDAYS') != '':
            _addldays = os.getenv('FOI_ADDITIONAL_HOLIDAYS')
            for _addlday in _addldays.split(","):
                ca_holidays.append(_addlday.strip().replace('XXXX',str(year)))
        return ca_holidays    

    def isbusinessday(self, inpdate, holidays=None):
        _holidays = self.getholidays() if holidays is None else holidays
        if datetimehandler().formatdate(inpdate) not in _holidays and self.__isweekday(inpdate) == True:
            return True
        return False

    def __isweekday(self, inpdate):
        _inpdate = datetimehandler().getdate(inpdate)
        if _inpdate.weekday() < 5:
            return True
        else:   
            return False 
    
    def __getpreviousweekday(self, cfrduedate):
        diff = 1
        _cfrduedate = datetimehandler().getdate(cfrduedate)  
        if _cfrduedate.weekday() == 0:
            diff = 3
        elif _cfrduedate.weekday() == 6:
            diff = 2
        else :
            diff = 1  
        res = _cfrduedate - timedelta(days=diff)
        return res.strftime(datetimehandler().getdefaultdateformat())           
   
    def __isholiday(self, input, ca_holidays):
        return input in ca_holidays   
      
