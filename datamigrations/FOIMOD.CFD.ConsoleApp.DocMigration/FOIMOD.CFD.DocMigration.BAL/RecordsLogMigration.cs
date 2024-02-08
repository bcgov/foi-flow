using Amazon.Runtime.Internal.Util;
using Amazon.S3;
using FOIMOD.CFD.DocMigration.DAL;
using FOIMOD.CFD.DocMigration.Models;
using FOIMOD.CFD.DocMigration.Models.Document;
using FOIMOD.CFD.DocMigration.Models.FOIFLOWDestination;
using FOIMOD.CFD.DocMigration.Utils;
using MCS.FOI.OCRtoPDF;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Logging;
using System.Data;
using ILogger = Microsoft.Extensions.Logging.ILogger;


namespace FOIMOD.CFD.DocMigration.BAL
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
            DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher();
            OCRTOPdf.TessaractPath = "C:\\Abindev\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR\\Tesseractbinaries_core\\Windows\\x64";
            OCRTOPdf.TessaractLanguagePath = "C:\\Abindev\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR\\tessdata";

            ilogger.LogInformation("Inside Records Log migration process, Starting migration loop of Records Logs");
           
            
            var requestswithquotes = this.RequestsToMigrate.Split(',');

            foreach (var requestwithquote in requestswithquotes)
            {
                var _requestnumber = requestwithquote.Replace("'", "");
                try
                {
                   

                    ilogger.LogInformation(string.Format("Starting migration of REQUEST {0}", _requestnumber));

                    List<DocumentToMigrate>? records = documentsDAL.GetRecordsByRequest(_requestnumber);



                    if (records.Any())
                    {
                        var docIDs = records.Select(r => r.IDocID).Distinct().ToList();

                        ilogger.LogInformation(string.Format("Found {0} Records migration for REQUEST {0}", docIDs.Count(), _requestnumber));

                        foreach (var docid in docIDs)
                        {
                          
                            var actualfilename =string.Empty;
                            try
                            {
                                var pagesbyDoc = records.Where(r => r.IDocID == docid).OrderBy(p => p.PageSequenceNumber).ToList();
                                var pagedetails = pagesbyDoc.First();
                                actualfilename = string.Format("{0}_Page_{1}{2}", pagedetails.FolderName, pagedetails.TotalPageCount, pagedetails.FileType);
                                if (pagesbyDoc.Any() && pagesbyDoc.Count == 1) // SINGLE PAGE DOC
                                {
                                    
                                    //TODO: FIND SECTION TAG - LOGIC TODO
                                    

                                }
                                else if (pagesbyDoc.Any() && pagesbyDoc.Count > 1) // MULTIPLE PAGES DOC
                                {
                                    //TODO: FIND SECTION TAG - LOGIC TODO
                                  
                                  
                                    //STITCHING PDF
                                    var baseRecordsLocation = Path.Combine(SystemSettings.FileServerRoot, SystemSettings.RecordsbaseFolder);
                                    MemoryStream docStream = pagedetails.FileType.ToLower().Contains("pdf") ? docMigrationPDFStitcher.MergePDFs(pagesbyDoc, baseRecordsLocation) : docMigrationPDFStitcher.MergeImages(pagesbyDoc);


                                    if (docStream != null)
                                    {

                                        using (MemoryStream stitchedFileStream = OCRTOPdf.ConvertToSearchablePDF(docStream))
                                        {
                                            var destinationfilename_guidbased = string.Format("{0}{1}", Guid.NewGuid().ToString(), pagedetails.FileType);
                                            var s3filesubpath = string.Format("{0}/{1}", SystemSettings.MinistryRecordsBucket, _requestnumber.ToUpper());

                                            var uploadresponse = await docMigrationS3Client.UploadFileAsync(new UploadFile() { AXISRequestID = _requestnumber.ToUpper(), SubFolderPath = s3filesubpath, DestinationFileName = destinationfilename_guidbased, FileStream = stitchedFileStream });

                                        }
                                    }

                                }
                            }
                            catch(Exception ex)
                            {
                                string exception = string.Format("Error happened while processing document, {0}, with DOCID {1}, on Request {2} and Error details as : ", actualfilename, docid, _requestnumber, ex.Message);
                                ilogger.LogError(exception);
                                throw new Exception(exception);
                            }
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
