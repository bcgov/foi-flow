using Azure.Core;
using FOIMOD.CFD.DocMigration.Models.Document;
using Microsoft.Data.SqlClient;
using Microsoft.Identity.Client;
using System.Data;

namespace FOIMOD.CFD.DocMigration.DAL
{
    public class DocumentsDAL
    {

        private SqlConnection sqlConnection;
        public DocumentsDAL(SqlConnection _sqlConnection)
        {
            sqlConnection = _sqlConnection;
        }

        public List<DocumentToMigrate> GetDocumentsToMigrate(string requestNumber)
        {

            using (SqlDataAdapter sqlSelectCommand = new(query, sqlConnection))
            {
                sqlSelectCommand.SelectCommand.Parameters.Add("@vcVisibleRequestID", SqlDbType.VarChar, 50).Value = request;
                try
                {
                    sqlConnection.Open();
                    sqlSelectCommand.Fill(dataTable);
                }
                catch (SqlException ex)
                {
                    Ilogger.Log(LogLevel.Error, ex.Message);
                    throw;
                }
                catch (Exception e)
                {
                    Ilogger.Log(LogLevel.Error, e.Message);
                    throw;
                }

            }

    }
}