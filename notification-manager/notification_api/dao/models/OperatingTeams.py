from notification_api.dao.db import getconnection
import logging

class OperatingTeam:


    @classmethod
    def gettype(cls, team):   
        conn = None 
        try:
            _notificationtypes = []
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute("""select type from "OperatingTeams" ot where replace(lower(name),' ','') = replace('{0}',' ','')""".format(team))
            data = cursor.fetchone()
            if data is not None:
               return  data

            cursor.close()
            return _notificationtypes
        except(Exception) as error:
            logging.error(error)
        finally:
            if conn:
                conn.close()

    
