from datetime import datetime
from notification_api.dao.db import getconnection
import logging
from marshmallow import EXCLUDE, Schema, fields, validate
import json


class FOIRequestNotification(object):

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE
    requestid = fields.Int(data_key="requestid") 
    idnumber = fields.Str(data_key="idnumber")
    foirequestid = fields.Int(data_key="foirequestid") 
    notificationtypelabel = fields.Int(data_key="notificationtypelabel") 
    axisnumber = fields.Str(data_key="axisnumber")
    version = fields.Int(data_key="version")
    notification = fields.Str(data_key="notification")
    createdby = fields.Str(data_key="createdby")
    created_at = fields.Str(data_key="created_at")
    
    def savenotification(self, notificationschema):
        conn = None
        try:
            id_of_new_row = None
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO public."FOIRequestNotifications" (notification, notificationtypelabel, requestid, "version", idnumber, axisnumber, foirequestid, createdby, created_at) \
                                VALUES(%s::json,%s::integer, %s::integer, %s::integer,%s,%s,%s::integer,%s,%s) RETURNING notificationid', 
                                (json.dumps(notificationschema.notification), int(notificationschema.notificationtypelabel), int(notificationschema.requestid), int(notificationschema.version),
                                 str(notificationschema.idnumber), str(notificationschema.axisnumber), int(notificationschema.foirequestid), str(notificationschema.createdby), datetime.now()))
            
            conn.commit()
            id_of_new_row = cursor.fetchone()[0]
            cursor.close()
            return id_of_new_row            
        except(Exception) as error:
            logging.error(error)
        finally:
            if conn:
                conn.close()
            
    
