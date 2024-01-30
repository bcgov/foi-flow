using System.Data;
using System.Data.Common;
using System.Data.Odbc;


namespace FOIMOD.CFD.DocMigration.FOIFLOW.DAL
{
    public class RecordsDAL
    {
        private IDbConnection dbConnection;
        public RecordsDAL(IDbConnection _dbConnection)
        {
            dbConnection = _dbConnection;
        }

        /// <summary>
        /// RECORDS upload
        /// </summary>
        /// <param name="axisrequestnumber"></param>
        /// <param name="s3filepath"></param>
        /// <param name="actualfilename"></param>
        /// <param name="batchnumber"></param>
        /// <param name="migrationdatetime"></param>
        /// <param name="sectiondivisionid"></param>
        /// <param name="filesize"></param>
        /// <returns></returns>
        public bool InsertIntoFOIRequestRecords(string axisrequestnumber, string s3filepath, string actualfilename, string documentattributeJSON)
        {
            bool result = false;
            try
            {
                dbConnection.Open();
                var cmdString = @"DO $$ DECLARE requestnumber VARCHAR; BEGIN requestnumber := '{0}' ; INSERT INTO public.""FOIRequestRecords""(version, foirequestid, ministryrequestid, ministryrequestversion, filename, s3uripath, createdby, created_at,  attributes, isactive) VALUES (1, (SELECT foirequest_id FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), (SELECT foiministryrequestid FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), (SELECT version FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), '{1}', '{2}', 'migrationservice', NOW(), '{3}', true);END $$";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbConnection;
                   
                    comm.CommandText = string.Format(cmdString, axisrequestnumber, actualfilename, s3filepath, documentattributeJSON);
                    comm.CommandType = CommandType.Text;
                    comm.ExecuteNonQuery();
                    dbConnection.Close();
                    result = true;
                }
            }
            catch (Exception ex)
            {
                dbConnection.Close();
                result = false;
                throw;
            }
            return result;
        }

    }
}
