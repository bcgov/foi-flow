from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy import text
import logging
from dateutil.parser import parse


class factRequestExtensions(db.Model):
    __tablename__ = 'factRequestExtensions' 
    # Defining the columns
    foirequestid = db.Column(db.Integer, primary_key=True,autoincrement=True)

    @classmethod
    def getextensionsbyrequestid(cls, requestid):        
        extensions = []
        try:
            sql = """SELECT 
                    et.extensiontypename,            
                    re.extensiondays,    
                    re.extendeddate,
                    re.approveddate,
                    approvedstatus,
                    re.createddate
                FROM public."factRequestExtensions" re
				join public."dimExtensionTypes" et on et.extensiontypeid = re.extensiontypeid
                where foirequestid = (select foirequestid from public."ClosedRequestDetailsPost2018" where visualrequestfilenumber = :requestid) 
                and re.activeflag = 'Y'
                and re.runcycleid in (
                select max(runcycleid) from public."factRequestExtensions"
                where foirequestid = (select foirequestid from public."ClosedRequestDetailsPost2018" where visualrequestfilenumber = :requestid)
                group by requestextid
                )
            ORDER BY foirequestid DESC, runcycleid DESC, requestextid DESC"""
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                extension = {}
                extension["approvednoofdays"] = row['extensiondays']
                extension["extendedduedays"] = row['extensiondays']
                extension["created_at"] = row['createddate'].strftime('%Y-%m-%d')
                extension["extendedduedate"] = row['extendeddate'].strftime('%Y-%m-%d')
                extension["extensionreson"] = row['extensiontypename']
                extension["extensionstatus"] = row['approvedstatus']
                extensions.append(extension)
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return extensions
    
    