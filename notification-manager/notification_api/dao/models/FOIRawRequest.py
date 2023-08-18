from notification_api.dao.db import getconnection
import logging

class FOIRawRequest:


    @classmethod 
    def getrequest(cls, requestid):
        conn = None
        try:
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute("""select requestid ,  "version" , axisrequestid  from "FOIRawRequests" fr  where requestid  = {0} order by "version" desc limit  1;""".format(requestid))
            data = cursor.fetchall()
            for row in data:
                return {"requestid": row["requestid"],"version": row["version"],"axisrequestid": row["axisrequestid"]}
            cursor.close()
            return None
        except(Exception) as error:
            logging.error(error)
            raise   
        finally:
            if conn:
                conn.close()

    @classmethod 
    def getwatchers(cls, requestid):
        conn = None
        try:
            watchers = []
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute("""select distinct on (watchedby, watchedbygroup) watchedby, watchedbygroup, isactive 
                                from "FOIRawRequestWatchers" where requestid={0} 
                                order by watchedby, watchedbygroup, created_at desc""".format(requestid))
            data = cursor.fetchall()
            for row in data:
               if bool(row[2]) == True:
                    watchers.append({"watchedby": str(row[0]), "watchedbygroup": str(row[1])}) 

            cursor.close()
            return watchers
        except(Exception) as error:
            logging.error(error)
        finally:
            if conn:
                conn.close()

        
    @classmethod 
    def getcommentusers(cls, commentid):
        users = []
        conn = None
        try:
            users = []
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute("""select commentid, createdby, taggedusers from (
                    select commentid, commenttypeid, createdby, taggedusers from "FOIRawRequestComments" frc   where commentid = (select parentcommentid from "FOIRawRequestComments" frc   where commentid={0})
                    union all 
                    select commentid, commenttypeid, createdby, taggedusers from "FOIRawRequestComments" frc   where commentid <> {0} and parentcommentid = (select parentcommentid from "FOIRawRequestComments" frc   where commentid={0})
                ) cmt where commenttypeid =1""".format(commentid))
            data = cursor.fetchall()
            for row in data:
                users.append({"commentid": row["commentid"], "createdby": row["createdby"], "taggedusers": row["taggedusers"]}) 
            cursor.close()
            return users
        except(Exception) as error:
            logging.error(error)
        finally:
            if conn:
                conn.close()