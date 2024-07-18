using System.Data;
using System.Data.Odbc;

using FOIMOD.HistoricalDocMigration.Models.FOIFLOWDestination;

namespace FOIMOD.HistoricalDocMigration.DocMigration.FOIFLOW.DAL
{
    public class HistoricalRecordsDAL
    {
        private IDbConnection dbConnection;
        public HistoricalRecordsDAL(IDbConnection _dbConnection)
        {
            dbConnection = _dbConnection;
        }

        /// <summary>
        /// Attachments insert - Correspondence logs goes here
        /// </summary>
        /// <param name="s3filepath"></param>
        /// <param name="actualfilename"></param>
        /// <param name="axisrequestnumber"></param>
        /// <returns></returns>
        public bool InsertIntoHistoricalRecords(HistoricalRecords historicalRecords )
        {
            bool result = false;
            try
            {
                dbConnection.Open();
                var cmdString = @"INSERT INTO public.""HistoricalRecords"" (recordfilename,displayfilename, description, axisrequestid, s3uripath, createdby, created_at,  iscorresponcedocument,attributes) VALUES ('{0}','{1}', '{2}', '{3}','{4}','{5}', NOW(), {6},'{7}');";
                using (OdbcCommand comm = new OdbcCommand())
                {
                    comm.Connection = (OdbcConnection)dbConnection;
                    comm.CommandText = string.Format(cmdString, historicalRecords.RecordFileName, historicalRecords.DisplayFileName, historicalRecords.Description,historicalRecords.AXISRequestID,historicalRecords.S3Path,historicalRecords.CreatedBy,historicalRecords.IsCorrenpondenceDocument,historicalRecords.Attributes);                    
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