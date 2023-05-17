from datetime import datetime
from notification_api.dao.db import getconnection
import logging


class NotificationType(object):

    def getid(self, name):
        try:
            _notificationtypes = []
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute("""select notificationtypeid  from "NotificationTypes" nt  where isactive = true and name = '{0}'""".format(name))
            data = cursor.fetchone()
            if data is not None:
               return  data[0]

            cursor.close()
            return _notificationtypes
        except(Exception) as error:
            logging.error(error)
            raise   
        finally:
            conn.close()


