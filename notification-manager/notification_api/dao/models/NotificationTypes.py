from datetime import datetime
from notification_api.dao.db import getconnection
import logging


class NotificationType(object):

    def getid(self, name):
        conn = None
        try:
            _notificationtypes = []
            conn = getconnection()
            cursor = conn.cursor()
            print("name", name)
            cursor.execute("""select notificationtypelabel, notificationtypeid  from "NotificationTypes" nt  where isactive = true and name = '{0}'""".format(name))
            data = cursor.fetchone()
            if data is not None:
               data = {"notificationtypelabel": data[0], "notificationtypeid": data[1]}
               return  data

            cursor.close()
            return _notificationtypes
        except(Exception) as error:
            logging.error(error)
        finally:
            if conn:
                conn.close()


