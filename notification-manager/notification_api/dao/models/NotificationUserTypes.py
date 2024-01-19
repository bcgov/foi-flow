'''
This file is used in the notification manager container 
to fetch the data models for the NotificationUserTypes table
'''
from datetime import datetime
from notification_api.dao.db import getconnection
import logging

class NotificationUserType(object):
    def getid(self, name):
        conn = None
        try:
            _notificationusertypes = []
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute("""select notificationusertypelabel, notificationusertypeid  from "NotificationUserTypes" nt  where isactive = true and name = '{0}'""".format(name))
            data = cursor.fetchone()
            if data is not None:
               data = {"notificationusertypelabel": data[0], "notificationusertypeid": data[1]}
               return  data

            cursor.close()
            return _notificationusertypes
        except(Exception) as error:
            logging.error(error)
        finally:
            if conn:
                conn.close()
    
    def getidbylabel(self, label):
        conn = None
        try:
            _notificationusertypes = []
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute("""select notificationusertypeid  from "NotificationUserTypes" nt  where isactive = true and notificationusertypelabel = '{0}'""".format(label))
            data = cursor.fetchone()
            if data is not None:
               data = {"notificationusertypeid": data[0]}
               return  data

            cursor.close()
            return _notificationusertypes
        except(Exception) as error:
            logging.error(error)
        finally:
            if conn:
                conn.close()
