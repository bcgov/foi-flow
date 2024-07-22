using Amazon.S3;
using FOIMOD.HistoricalDocMigration.AXIS.DAL;
using FOIMOD.HistoricalDocMigration.DocMigration.FOIFLOW.DAL;
using FOIMOD.HistoricalDocMigration.Models;
using FOIMOD.HistoricalDocMigration.Models.Document;
using FOIMOD.HistoricalDocMigration.Models.FOIFLOWDestination;
using FOIMOD.HistoricalDocMigration.Utils;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Logging;
using System.Data;
using System.Data.Odbc;
using System.Net.Mail;
using ILogger = Microsoft.Extensions.Logging.ILogger;


namespace FOIMOD.HistoricalDocMigration.DocMigration.BAL
{
    public class RecordsLogMigration
    {


        private IDbConnection sourceaxisSQLConnection;
        private IDbConnection destinationfoiflowQLConnection;
        
        private IAmazonS3 amazonS3;
        private ILogger ilogger;

        public string RequestsToMigrate { get; set; }
        public RecordsLogMigration(IDbConnection _sourceAXISConnection, IDbConnection _destinationFOIFLOWDB, IAmazonS3 _amazonS3, ILogger _logger)
        {
            sourceaxisSQLConnection = _sourceAXISConnection;
            destinationfoiflowQLConnection = _destinationFOIFLOWDB;
         
            amazonS3 = _amazonS3;
            ilogger = _logger;
        }





        public async Task RunMigration()
        {
            DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3);

            DocumentsDAL documentsDAL = new DocumentsDAL((SqlConnection)sourceaxisSQLConnection);

            HistoricalRecordsDAL recordsDAL = new HistoricalRecordsDAL((OdbcConnection)destinationfoiflowQLConnection);


            DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher();



            ilogger.LogInformation("Inside Records Log migration process, Starting migration loop of Records Logs");


            var requestswithquotes = this.RequestsToMigrate.Split(',');

            foreach (var requestwithquote in requestswithquotes)
            {
                var _requestnumber = requestwithquote.Replace("'", "");
                try
                {


                    ilogger.LogInformation(string.Format("Starting migration of REQUEST {0}", _requestnumber));

                    List<DocumentToMigrate>? records = documentsDAL.GetRecordsByRequest(_requestnumber);



                    if (records !=null && records.Any())
                    {
                        var year = records.First().ClosingDate.Value.Year;
                        var month = records.First().ClosingDate.Value.Month;
                        

                        var docIDs = records.Select(r => r.IDocID).Distinct().ToList();

                        ilogger.LogInformation(string.Format("Found {0} Records migration for REQUEST {0}", docIDs.Count(), _requestnumber));

                        foreach (var docid in docIDs)
                        {
                            ilogger.LogInformation("###################################################################################");
                            ilogger.LogInformation(string.Format("Processing document ID {0} for request {1}", docid, _requestnumber));
                            var actualfilename = string.Empty;
                            try
                            {
                                var baseRecordsLocation = Path.Combine(SystemSettings.FileServerRoot, SystemSettings.RecordsbaseFolder);
                                var pagesbyDoc = records.Where(r => r.IDocID == docid).OrderBy(p => p.PageSequenceNumber).ToList();
                                var hasanyimage = pagesbyDoc.Where(r => r.FileType.ToLower().EndsWith("png") || r.FileType.ToLower().EndsWith("jpeg") || r.FileType.ToLower().EndsWith("jpg")).Any();
                                var pagedetails = pagesbyDoc.First();
                                
                                actualfilename = string.Format("{0}_{1}{2}", pagedetails.ParentFolderName?.Replace("'", ""), pagedetails.FolderName?.Replace("'", ""), ".pdf");
                                if (pagesbyDoc.Any())
                                {

                                    //STITCHING PDF
                                    ilogger.LogInformation(string.Format("Stitching started for pages of  document ID {0} for request {1}, page count is {2}, started at {3}", docid, _requestnumber, pagedetails.TotalPageCount, DateTime.Now));
                                    using HugeMemoryStream docStream = !hasanyimage ? docMigrationPDFStitcher.MergePDFs(pagesbyDoc, baseRecordsLocation) : docMigrationPDFStitcher.MergeImages(pagesbyDoc, baseRecordsLocation);
                                    ilogger.LogInformation(string.Format("Stitching COMPLETED!! for pages of  document ID {0} for request {1}, page count is {2}, end at {3}", docid, _requestnumber, pagedetails.TotalPageCount, DateTime.Now));

                                    if (docStream != null)
                                    {
                                        // ilogger.LogInformation(string.Format("OCR starting for pages of  document ID {0} for request {1}, page count is {2}, started at {3}", docid, _requestnumber, pagedetails.TotalPageCount, DateTime.Now));
                                        //using (MemoryStream stitchedFileStream = OCRTOPdf.ConvertToSearchablePDF(docStream))
                                        using (HugeMemoryStream stitchedFileStream = docStream)
                                        {

                                            var destinationfilename_guidbased = string.Format("{0}{1}", Guid.NewGuid().ToString(), ".pdf");
                                           // var s3filesubpath = string.Format("{0}/{1}", SystemSettings.MinistryRecordsBucket, _requestnumber.ToUpper());
                                            var s3filesubpath = string.Format("{0}/{1}/{2}/{3}/{4}", SystemSettings.S3_Attachements_BasePath, "CFR", year, month, records.First().AXISRequestNumber);
                                            // ilogger.LogInformation(string.Format("OCR completed for pages of  document ID {0} for request {1}, page count is {2}, ended at {3}", docid, _requestnumber, pagedetails.TotalPageCount, DateTime.Now));

                                            ilogger.LogInformation(string.Format("Upload starting for  document ID {0} for request {1}, page count is {2}, started at {3}", docid, _requestnumber, pagedetails.TotalPageCount, DateTime.Now));

                                            var historicalcorrespondencelog = new HistoricalRecords() { AXISRequestID = _requestnumber.ToUpper(), IsCorrenpondenceDocument = false, S3Subfolder = s3filesubpath, S3Path = s3filesubpath, RecordFileName = destinationfilename_guidbased, FileStream = stitchedFileStream, DisplayFileName = FilePathUtils.CleanFileNameInput(actualfilename)};


                                            var uploadresponse = await docMigrationS3Client.UploadFileAsync(historicalcorrespondencelog);

                                            if (uploadresponse != null && uploadresponse.IsSuccessStatusCode)
                                            {

                                                ilogger.LogInformation(string.Format("Upload successful for   document ID {0} for request {1}, page count is {2}, completed at {3}", docid, _requestnumber, pagedetails.TotalPageCount, DateTime.Now));

                                                ilogger.LogInformation(string.Format("DB Metadata updates started for  document ID {0} for request {1}, page count is {2}, started at {3}", docid, _requestnumber, pagedetails.TotalPageCount, DateTime.Now));

                                                int.TryParse(pagedetails.TotalPageCount, out int pagecount);
                                                var documenthash = Guid.NewGuid().ToString().Replace("-", "");
                                                var batch = Guid.NewGuid().ToString();
                                                var s3url = string.Format("{0}/{1}/{2}", SystemSettings.S3_EndPoint, s3filesubpath, destinationfilename_guidbased);
                                                // byte[] fileData = stitchedFileStream.Length
                                                long filesize = stitchedFileStream.Length; //TODO: Need to find out the  KB or B or MB in DB

                                                string attributesJSONtemplate = @"{{""iDocID"": {0}, ""siFolderID"": ""{1}""}}";
                                                var attributedJSON = string.Format(attributesJSONtemplate, docid, pagedetails.SiFolderID);
                                                historicalcorrespondencelog.Attributes = attributedJSON;

                                                var recordid = recordsDAL.InsertIntoHistoricalRecords(historicalcorrespondencelog);


                                                ilogger.LogInformation(string.Format("DB Metadata updates COMPLETED for  document ID {0} for request {1}, page count is {2}, completed at {3}", docid, _requestnumber, pagedetails.TotalPageCount, DateTime.Now));

                                            }

                                        }


                                    }
                                }

                            }

                            catch (Exception ex)
                            {
                                string exception = string.Format("Record Log Migration ,Error happened while processing document, {0}, with DOCID {1}, on Request {2} and Error details as :{3} ", actualfilename, docid, _requestnumber, ex.Message);
                                ilogger.LogError(exception);
                                //throw new Exception(exception);
                            }
                            docMigrationPDFStitcher.Dispose();
                            ilogger.LogInformation("#####################################################################################");
                            ilogger.LogInformation(Environment.NewLine);
                        }

                    }
                }
                catch (Exception ex)
                {
                    //TODO : LOG EXPECTION with REQUEST NUMBER, DOCID, AXIS FOLDER etc
                    ilogger.LogError(string.Format("{0}, Error is {1}", _requestnumber, ex.Message));
                }

            }

            ilogger.LogInformation("Inside Records Log migration process, COMPLETED migration loop of Records Logs");
        }
    }
}
