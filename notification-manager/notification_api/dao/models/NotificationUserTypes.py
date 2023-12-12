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
            cursor.execute("""select notificationusertypelabel  from "NotificationUserTypes" nt  where isactive = true and name = '{0}'""".format(name))
            data = cursor.fetchone()
            if data is not None:
               return  data[0]

            cursor.close()
            return _notificationusertypes
        except(Exception) as error:
            logging.error(error)
        finally:
            if conn:
                conn.close()
