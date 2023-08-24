using System.Data;
using System.Data.Common;
using System.Data.Odbc;

namespace FOIMOD.CFD.DocMigration.FOIFLOW.DAL
{
    public class AttachmentsDAL
    {
        private IDbConnection dbConnection;
        public AttachmentsDAL(IDbConnection _dbConnection)
        {
            dbConnection = _dbConnection;
        }

        public bool InsertIntoMinistryRequestDocuments(string s3filepath, string actualfilename, string axisrequestnumber)
        {
            bool result = false;
            try
            {
                dbConnection.Open();
                var cmdString = @"DO $$ DECLARE requestnumber VARCHAR; BEGIN requestnumber := '{0}' ; INSERT INTO public.""FOIMinistryRequestDocuments"" ( documentpath, created_at, createdby,  foiministryrequest_id, foiministryrequestversion_id, filename, isactive, category, version) VALUES ('{1}', NOW(), 'cfdmigration',  (SELECT foiministryrequestid FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), (SELECT version FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), '{2}', True, 'applicant', 1); END $$";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbConnection;
                    comm.CommandText = string.Format(cmdString,axisrequestnumber,s3filepath,actualfilename);                    
                    comm.CommandType = CommandType.Text;
                    comm.ExecuteNonQuery();
                    dbConnection.Close();
                    result = true;
                }
            }
            catch (Exception ex) {
                dbConnection.Close();
                result = false;
                throw;
            }
            return result;
        }
        


    }
}