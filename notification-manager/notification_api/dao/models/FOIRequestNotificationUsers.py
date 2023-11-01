from datetime import datetime
from notification_api.dao.db import getconnection
import logging
from marshmallow import EXCLUDE, Schema, fields, validate
import json

class FOIRequestNotificationUser(object):
    
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE
    notificationid = fields.Int(data_key="notificationid") 
    userid = fields.Str(data_key="userid")
    notificationusertypeid = fields.Int(data_key="notificationusertypeid") 
    createdby = fields.Str(data_key="createdby")
    created_at = fields.Str(data_key="created_at")

    def savenotificationuser(self, notificationuser):
        conn = None
        try:
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO public."FOIRequestNotificationUsers" (notificationid, userid, notificationusertypeid, createdby, created_at) \
                                VALUES(%s::integer,%s, %s::integer, %s,%s)', 
                                (int(notificationuser.notificationid), str(notificationuser.userid), int(notificationuser.notificationusertypeid),  str(notificationuser.createdby), datetime.now()))
            conn.commit()
            cursor.close()
        except(Exception) as error:
            logging.error(error)
        finally:
            if conn:
                conn.close()
            
