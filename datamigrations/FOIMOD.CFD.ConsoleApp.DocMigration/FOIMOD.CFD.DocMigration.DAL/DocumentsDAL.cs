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


        private string recordsbyrequestid = @"
                        DECLARE @SectionList VARCHAR(MAX);
                        DECLARE @irequestid INT
                        SET @irequestid=(SELECT TOP 1 iRequestID FROM tblRequests WHERE vcVisibleRequestID = '{0}')
                    SET @SectionList = NULL;
                    SELECT
                        @SectionList = COALESCE(@SectionList+':', '')+vcSectionList
                    FROM [dbo].[tblDocumentReviewLog] WHERE iRequestID =@irequestid

                    SELECT D.iDocID,D.tiSections,vcFileName as FilePath,D.siFolderID,D.siPageCount ,p.siPageNum FROM tblPages P inner join tblDocuments D on P.iDocID=D.iDocID 
					
					WHERE  D.iDocID in(
                    --- Review Log Documents
                    SELECT iDocID FROM [dbo].[tblDocumentReviewLog] WHERE iRequestID = @irequestid
                    union
                    SELECT iDocID FROM tblDocuments d with(nolock) where iDocID IN (SELECT Data FROM [dbo].[AFX_Splitter](@SectionList, ':'))
                    union
                    --- Request Folder Documents    
                    select iDocID from tblRedactionLayers where irequestid=@irequestid AND iDeliveryID is NULL
                    )";

        private string getQueryByType(DocumentTypeFromAXIS documentTypeFromAXIS, string requestnumber="")
        {
            var query = string.Empty;
            switch (documentTypeFromAXIS) {

                case DocumentTypeFromAXIS.CorrespondenceLog:
                    query = correspondencelog;
                    break;
                case DocumentTypeFromAXIS.RequestRecords:
                    query = string.Format(recordsbyrequestid, requestnumber);
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


        public List<DocumentToMigrate>? GetRecordsByRequest(string requestnumber)
        {
            List<DocumentToMigrate> documentToMigrates = null;
            using (SqlDataAdapter sqlSelectCommand = new(getQueryByType(DocumentTypeFromAXIS.RequestRecords,requestnumber), sqlConnection))
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
                                IDocID= Convert.ToInt32(row["iDocID"]),                                
                                PageFilePath = Convert.ToString(row["FilePath"]),
                                SiFolderID = Convert.ToString(row["siFolderID"]),
                                TotalPageCount = Convert.ToString(row["siPageCount"]),
                                PageSequenceNumber = Convert.ToInt32(row["siPageNum"]),
                                AXISRequestNumber = requestnumber.ToUpper(),
                                DocumentType = DocumentTypeFromAXIS.RequestRecords
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