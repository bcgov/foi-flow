using FOIMOD.HistoricalDocMigration.Models.AXISSource;
using FOIMOD.HistoricalDocMigration.Models.Document;
using Microsoft.Data.SqlClient;
using System.Data;

namespace FOIMOD.HistoricalDocMigration.AXIS.DAL
{

    public class DocumentsDAL
    {

        private SqlConnection sqlConnection;
        public DocumentsDAL(SqlConnection _sqlConnection)
        {
            sqlConnection = _sqlConnection;
        }

        private string correspondencelog = @"

                        

                            SELECT R.vcVisibleRequestID, 'RP' AS FileType, '' as vcSubject, GETDATE() as sdtMailedDate, '' as vcEmail, '' as vcFromEmail, '' as emailbody, RD.vcPath as attachments, R.sdtClosedDate as ClosingDate 
                            FROM [dbo].[tblRequestResponsiveDocs] RD JOIN tblRequests R on RD.iRequestID = R.iRequestID WHERE R.vcVisibleRequestID in ({0})
                            UNION ALL
                            SELECT          R.vcVisibleRequestID,
											'CL' AS FileType
                                            , C.vcSubject
                                            ,C.sdtMailedDate
                                            ,C.vcEmail
                                            ,C.vcFromEmail
                                            , CAST(C.vcBody as NVARCHAR(max)) as emailbody
                                            , STRING_AGG(CAST((C.vcFilePath +' * ' +C.vcFileName) as nvarchar(max)),' | ') as attachments
                                            , R.sdtClosedDate as ClosingDate

                                            FROM tblCorrespondence C JOIN tblRequests R on C.iRequestID = R.iRequestID
                                            WHERE R.vcVisibleRequestID in ({1})

                                            GROUP BY R.vcVisibleRequestID,C.vcSubject,C.sdtMailedDate,C.vcEmail,C.vcFromEmail,CAST(C.vcBody as NVARCHAR(max)),R.sdtClosedDate



                    ";


        private string recordsbyrequestid = @"
                        
                     DECLARE @SectionList VARCHAR(MAX);
                     DECLARE @SectionListRL VARCHAR(MAX);
                     DECLARE @irequestid INT
                     DECLARE @closingdate DATE

                          SET @irequestid=(SELECT TOP 1 iRequestID FROM tblRequests WHERE vcVisibleRequestID = '{0}')
                          SET  @closingdate=(SELECT sdtClosedDate FROM tblRequests WHERE vcVisibleRequestID = '{1}')
                          SET @SectionList = NULL;

	                      IF NOT EXISTS (SELECT irequestid FROM [dbo].[tblRequestResponsiveDocs] WHERE iRequestID=@irequestid) 

                            BEGIN
                              SELECT
                                  @SectionList = COALESCE(@SectionList+':', '')+vcSectionList
                              FROM [dbo].[tblDocumentReviewLog] WHERE iRequestID =@irequestid

                               SELECT
                                  @SectionListRL = COALESCE(@SectionList+':', '')+vcSectionList
                              FROM [dbo].[tblRedactionLayers] WHERE iRequestID =@irequestid

                              SELECT DISTINCT D.iDocID,D.siFolderID,D.vcDocName as FolderName,(SELECT vcDocName FROM tblDocuments where iDocID =D.iParentDocID) as ParentFolderName ,D.tiSections,vcFileName as FilePath,REVERSE(SUBSTRING(REVERSE(vcFileName),1,4)) as FileType,D.siFolderID,D.siPageCount ,p.siPageNum ,(SELECT vcInternalName FROM tblDocReviewFlags WHERE tiDocReviewFlagID = PRF.tiDocReviewFlagID ) as PageReviewFlag, @closingdate as ClosingDate FROM tblPages P inner join tblDocuments D on P.iDocID=D.iDocID 
                              LEFT JOIN tblPageReviewFlags PRF ON P.iPageID = PRF.iPageID
                              WHERE  D.iDocID in(                 
                              SELECT iDocID FROM tblDocuments d with(nolock) where iDocID IN (SELECT Data FROM [dbo].[AFX_Splitter](@SectionList, ':'))
                              union
                              --- Request Folder Documents    
                              select iDocID from tblRedactionLayers where irequestid=@irequestid AND iDeliveryID is NULL
                              union
                              (SELECT Data FROM [dbo].[AFX_Splitter](@SectionListRL, ':'))
                              ) 

                              END
                   
                ";

        private string getQueryByType(DocumentTypeFromAXIS documentTypeFromAXIS, string requestnumber="")
        {
            var query = string.Empty;
            switch (documentTypeFromAXIS) {

                case DocumentTypeFromAXIS.CorrespondenceLog:
                    query =string.Format(correspondencelog,requestnumber, requestnumber);
                    break;
                case DocumentTypeFromAXIS.RequestRecords:
                    query = string.Format(recordsbyrequestid, requestnumber, requestnumber);
                    break;
                default:
                    break;
            
            
            }

            return query;
        }

        public List<DocumentToMigrate>? GetCorrespondenceLogDocuments(string cs_requestnumbers)
        {
            List<DocumentToMigrate> documentToMigrates = null;
            using (SqlDataAdapter sqlSelectCommand = new(getQueryByType(DocumentTypeFromAXIS.CorrespondenceLog, cs_requestnumbers), sqlConnection))
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
                                CLFileType = Convert.ToString(row["FileType"]),
                                EmailContent = Convert.ToString(row["emailbody"]), 
                                EmailSubject= Convert.ToString(row["vcSubject"]),
                                EmailTo = Convert.ToString(row["vcEmail"]),
                                EmailFrom = Convert.ToString(row["vcFromEmail"]),
                                EmailDate = Convert.ToString(row["sdtMailedDate"]),
                                EmailAttachmentDelimitedString = Convert.ToString(row["attachments"]),
                                AXISRequestNumber = Convert.ToString(row["vcVisibleRequestID"]),
                                ClosingDate = Convert.ToDateTime(row["ClosingDate"])
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
                                DocumentType = DocumentTypeFromAXIS.RequestRecords,
                                FolderName = Convert.ToString(row["FolderName"]),
                                FileType = Convert.ToString(row["FileType"]),
                                ParentFolderName = Convert.ToString(row["ParentFolderName"]),
                                ReviewFlag = Convert.ToString(row["PageReviewFlag"]),
                                ClosingDate = Convert.ToDateTime(row["ClosingDate"])
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