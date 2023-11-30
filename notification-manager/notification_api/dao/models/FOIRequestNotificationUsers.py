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
    notificationusertypelabel = fields.Int(data_key="notificationusertypelabel") 
    createdby = fields.Str(data_key="createdby")
    created_at = fields.Str(data_key="created_at")
    isdeleted = fields.Boolean(data_key="isdeleted")

    def savenotificationuser(self, notificationuser):
        conn = None
        try:
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO public."FOIRequestNotificationUsers" (notificationid, userid, notificationusertypeid, notificationusertypelabel, createdby, created_at, isdeleted) \
                                VALUES(%s::integer, %s, %s::integer, %s, %s, %s::boolean)',
                                (int(notificationuser.notificationid), str(notificationuser.userid), int(notificationuser.notificationusertypeid), str(notificationuser.notificationusertypelabel), str(notificationuser.createdby), datetime.now(), int(notificationuser.isdeleted)))
            conn.commit()
            cursor.close()
        except(Exception) as error:
            logging.error(error)
        finally:
            if conn:
                conn.close()
            
