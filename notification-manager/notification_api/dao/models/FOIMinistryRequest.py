from notification_api.dao.db import getconnection
import logging


class FOIMinistryRequest:

    
    @classmethod 
    def getrequest(cls, ministryrequestid):
        try:
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute("""select foiministryrequestid, filenumber, foirequest_id, "version" , axisrequestid, assignedministryperson, assignedto 
                                from "FOIMinistryRequests" fr where foiministryrequestid  = {0} order by "version" desc limit  1""".format(ministryrequestid))
            row = cursor.fetchone()
            if row is not None:
                return {"foiministryrequestid": str(row[0]), "filenumber": row[1], "foirequest_id": row[2], "version": row[3], "axisrequestid": row[4], "assignedministryperson": row[5], "assignedto": row[6]}
            cursor.close()
            return None
        except(Exception) as error:
            logging.error(error)
            raise   
        finally:
            conn.close()

    @classmethod 
    def getwatchers(cls, ministryrequestid, query=None):
        try:
            watchers = []
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute("""select distinct on (watchedby, watchedbygroup) watchedby, watchedbygroup, isactive 
                                from "FOIRequestWatchers" where ministryrequestid={0} 
                                order by watchedby, watchedbygroup, created_at desc""".format(ministryrequestid))
            data = cursor.fetchall()
            for row in data:
                if ((query == "ministry" and "Ministry Team" in row["watchedbygroup"]) or (query == "non-ministry" and "Ministry Team" not in row["watchedbygroup"]) or query is None):
                    watchers.append({"watchedby": str(row[0]), "watchedbygroup": str(row[1])}) 
            cursor.close()
            return watchers
        except(Exception) as error:
            logging.error(error)
            raise   
        finally:
            conn.close()

    @classmethod 
    def getcommentusers(cls, commentid):
        users = []
        try:
            users = []
            conn = getconnection()
            cursor = conn.cursor()
            cursor.execute("""select commentid, createdby, taggedusers from (
                        select commentid, commenttypeid, createdby, taggedusers from "FOIRequestComments" frc   where commentid = (select parentcommentid from "FOIRequestComments" frc   where commentid={0})
                        union all 
                        select commentid, commenttypeid, createdby, taggedusers from "FOIRequestComments" frc   where commentid <> {0} and parentcommentid = (select parentcommentid from "FOIRequestComments" frc   where commentid={0})
                    ) cmt where commenttypeid =1""".format(commentid))
            data = cursor.fetchall()
            for row in data:
                users.append({"commentid": row["commentid"], "createdby": row["createdby"], "taggedusers": row["taggedusers"]}) 
            cursor.close()
            return users
        except(Exception) as error:
            logging.error(error)
            raise   
        finally:
            conn.close()