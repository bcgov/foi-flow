using Azure.Core;
using FOIMOD.CFD.DocMigration.Models.AXISSource;
using FOIMOD.CFD.DocMigration.Models.Document;
using Microsoft.Data.SqlClient;
using Microsoft.Identity.Client;
using System;
using System.Collections.Generic;
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

        private string correspondencelog = string.Format(@"SELECT 

                                            R.vcVisibleRequestID
                                            , C.vcSubject
                                            ,C.sdtMailedDate
                                            ,C.vcEmail
                                            ,C.vcFromEmail
                                            , CAST(C.vcBody as NVARCHAR(max)) as emailbody
                                            , STRING_AGG(CAST((C.vcFilePath +' # ' +C.vcFileName) as nvarchar(max)),' | ') as attachments  

                                            FROM tblCorrespondence C JOIN tblRequests R on C.iRequestID = R.iRequestID
                                            WHERE R.vcVisibleRequestID in ({0})

                                            GROUP BY R.vcVisibleRequestID,C.vcSubject,C.sdtMailedDate,C.vcEmail,C.vcFromEmail,CAST(C.vcBody as NVARCHAR(max))", "'CFD-2015-50011','CFD-2014-50119','CLB-2017-70004'");

        private string getQueryByType(DocumentTypeFromAXIS documentTypeFromAXIS)
        {
            var query = string.Empty;
            switch (documentTypeFromAXIS) {

                case DocumentTypeFromAXIS.CorrespondenceLog:
                    query = correspondencelog;
                    break;

                default:
                    break;
            
            
            }

            return query;
        }

        public List<DocumentToMigrate>? GetCorrespondenceLogDocuments()
        {
            List<DocumentToMigrate> documentToMigrates = null;
            using (SqlDataAdapter sqlSelectCommand = new(getQueryByType(DocumentTypeFromAXIS.CorrespondenceLog), sqlConnection))
            {                
                try
                {
                    sqlConnection.Open();
                    using DataTable dataTable = new();
                    sqlSelectCommand.Fill(dataTable);
                    if (!dataTable.HasErrors && dataTable.Rows.Count > 0)
                    {
                        documentToMigrates = new();
                        foreach (DataRow row in dataTable.Rows)
                        {
                            documentToMigrates.Add(new DocumentToMigrate() 
                            { 
                                EmailContent = Convert.ToString(row["emailbody"]), 
                                EmailSubject= Convert.ToString(row["vcSubject"]),
                                EmailTo = Convert.ToString(row["vcEmail"]),
                                EmailFrom = Convert.ToString(row["vcFromEmail"]),
                                EmailDate = Convert.ToString(row["sdtMailedDate"]),
                                EmailAttachmentDelimitedString = Convert.ToString(row["attachments"]),
                                AXISRequestNumber = Convert.ToString(row["vcVisibleRequestID"]),
                            });

                        }
                    }
                }
                catch (SqlException ex)
                {
                    
                    throw ex;
                }
                catch (Exception e)
                {                   
                    throw;
                }
                finally
                {
                    sqlConnection.Close();
                }

            }
            return documentToMigrates;
        }
    }
}