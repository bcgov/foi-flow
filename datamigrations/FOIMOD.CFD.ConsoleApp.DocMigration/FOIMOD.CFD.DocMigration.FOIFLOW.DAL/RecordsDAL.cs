using System.Data;
using System.Data.Common;
using System.Data.Odbc;


namespace FOIMOD.CFD.DocMigration.FOIFLOW.DAL
{
    public class RecordsDAL
    {
        private IDbConnection dbfoiflowConnection;
        private IDbConnection dbfoidocreviewerConnection;
        public RecordsDAL(IDbConnection _dbflowConnection, IDbConnection _dbdocreviwerConnection)
        {
            dbfoiflowConnection = _dbflowConnection;
            dbfoidocreviewerConnection = _dbdocreviwerConnection;
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
        public int InsertIntoFOIRequestRecords(string axisrequestnumber, string s3filepath, string actualfilename, string documentattributeJSON, int ministryrequestid, int ministryrequestversion)
        {
            bool result = false;
            int recordid = -1;
            try
            {
                dbfoiflowConnection.Open();
                var cmdString = @"DO $$ DECLARE requestnumber VARCHAR; BEGIN requestnumber := '{0}' ; 
                    INSERT INTO public.""FOIRequestRecords""(version, foirequestid, ministryrequestid, ministryrequestversion, filename, s3uripath, createdby, created_at,  attributes, isactive) VALUES (1, (SELECT foirequest_id FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), (SELECT foiministryrequestid FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), (SELECT version FROM public.""FOIMinistryRequests"" WHERE axisrequestid=requestnumber ORDER BY created_at DESC LIMIT 1), '{1}', '{2}', 'migrationservice', NOW(), '{3}', true);                    
                     END $$";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoiflowConnection;

                    comm.CommandText = string.Format(cmdString, axisrequestnumber, actualfilename, s3filepath, documentattributeJSON, ministryrequestid, ministryrequestversion, s3filepath);
                    comm.CommandType = CommandType.Text;
                    comm.ExecuteNonQuery();
                                                          
                }


                using(OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoiflowConnection;
                    var selectSQL = @"SELECT recordid FROM public.""FOIRequestRecords"" 
                    WHERE ministryrequestid={0} and ministryrequestversion={1} and s3uripath='{2}' and isactive=true and createdby='migrationservice' 
                    ORDER BY created_at DESC LIMIT 1;";

                    comm.CommandText = string.Format(selectSQL, ministryrequestid, ministryrequestversion, s3filepath);
                    comm.CommandType = CommandType.Text;
                    OdbcDataReader odbcDataReader = comm.ExecuteReader();
                    while (odbcDataReader.Read())
                    {

                        recordid = Convert.ToInt32(odbcDataReader["recordid"]);
                    }
                }
                result = true;
                dbfoiflowConnection.Close();
            }
            catch (Exception ex)
            {
                dbfoiflowConnection.Close();
                result = false;
                throw;
            }
            return recordid;
        }

        public (int, int) GetMinistryRequestDetails(string axisrequestnumber)
        {
            var retVal = (-1, -1);
            try
            {

                dbfoiflowConnection.Open();
                var cmdString = @"SELECT foiministryrequestid,version FROM public.""FOIMinistryRequests"" WHERE axisrequestid='{0}' ORDER BY created_at DESC LIMIT 1";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoiflowConnection;

                    comm.CommandText = string.Format(cmdString, axisrequestnumber);
                    comm.CommandType = CommandType.Text;

                    OdbcDataReader odbcDataReader = comm.ExecuteReader();

                    while (odbcDataReader.Read())
                    {

                        retVal = (Convert.ToInt32(odbcDataReader["foiministryrequestid"]), Convert.ToInt32(odbcDataReader["version"]));

                    }



                }
            }
            catch (Exception ex)
            {
                dbfoiflowConnection.Close();

                throw;
            }
            finally
            {
                dbfoiflowConnection.Close();

            }
            return retVal;
        }

        public int InsertIntoDocumentMaster(int ministryrequestid, string s3filepath, int foiflowrecordid)
        {
            int result = -1;
            try
            {
                dbfoidocreviewerConnection.Open();
                var cmdString = @"INSERT INTO public.""DocumentMaster""(
                                    filepath, ministryrequestid, recordid,  isredactionready, created_at, createdby)
                                    VALUES ('{0}', {1}, {2}, true, NOW(), 'migrationservice');";


                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoidocreviewerConnection;

                    comm.CommandText = string.Format(cmdString, s3filepath, ministryrequestid, foiflowrecordid);
                    comm.CommandType = CommandType.Text;
                    comm.ExecuteNonQuery();
                   
                   
                }

                var documentmasterSQL = @"SELECT documentmasterid FROM   public.""DocumentMaster"" WHERE createdby='migrationservice' AND recordid={0} AND filepath='{1}' AND ministryrequestid={2};";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbfoidocreviewerConnection;

                    comm.CommandText = string.Format(documentmasterSQL, foiflowrecordid, s3filepath, ministryrequestid);
                    comm.CommandType = CommandType.Text;
                    OdbcDataReader odbcDataReader = comm.ExecuteReader();

                    while (odbcDataReader.Read())
                    {
                        result = Convert.ToInt32(odbcDataReader["documentmasterid"]);
                    }
                    

                }

                dbfoidocreviewerConnection.Close();

            }
            catch (Exception ex)
            {
                dbfoidocreviewerConnection.Close();
                result = -1;
                throw;
            }
            return result;
        }
    }
}
