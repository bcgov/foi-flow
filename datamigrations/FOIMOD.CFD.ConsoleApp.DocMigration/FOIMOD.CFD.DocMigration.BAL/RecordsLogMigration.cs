using Amazon.Runtime.Internal.Endpoints.StandardLibrary;
using Amazon.Runtime.Internal.Util;
using Amazon.S3;
using FOIMOD.CFD.DocMigration.DAL;
using FOIMOD.CFD.DocMigration.FOIFLOW.DAL;
using FOIMOD.CFD.DocMigration.Models;
using FOIMOD.CFD.DocMigration.Models.Document;
using FOIMOD.CFD.DocMigration.Models.FOIFLOWDestination;
using FOIMOD.CFD.DocMigration.Utils;
using MCS.FOI.OCRtoPDF;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Primitives;
using SkiaSharp;
using System;
using System.Data;
using System.Data.Odbc;
using System.IO;
using ILogger = Microsoft.Extensions.Logging.ILogger;


namespace FOIMOD.CFD.DocMigration.BAL
{
    public class RecordsLogMigration
    {


        private IDbConnection sourceaxisSQLConnection;
        private IDbConnection destinationfoiflowQLConnection;
        private IDbConnection destinationDocreviewerConnection;
        private IAmazonS3 amazonS3;
        private ILogger ilogger;

        public string RequestsToMigrate { get; set; }
        public RecordsLogMigration(IDbConnection _sourceAXISConnection, IDbConnection _destinationFOIFLOWDB, IDbConnection _destinationdocreviewerDB, IAmazonS3 _amazonS3, ILogger _logger)
        {
            sourceaxisSQLConnection = _sourceAXISConnection;
            destinationfoiflowQLConnection = _destinationFOIFLOWDB;
            destinationDocreviewerConnection = _destinationdocreviewerDB;
            amazonS3 = _amazonS3;
            ilogger = _logger;
        }


        public async Task RunMigration()
        {
            DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3);

            DocumentsDAL documentsDAL = new DocumentsDAL((SqlConnection)sourceaxisSQLConnection);

            RecordsDAL recordsDAL = new RecordsDAL((OdbcConnection)destinationfoiflowQLConnection, (OdbcConnection)destinationDocreviewerConnection);


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

                            var actualfilename = string.Empty;
                            try
                            {
                                var baseRecordsLocation = Path.Combine(SystemSettings.FileServerRoot, SystemSettings.RecordsbaseFolder);
                                var pagesbyDoc = records.Where(r => r.IDocID == docid).OrderBy(p => p.PageSequenceNumber).ToList();
                                var pagedetails = pagesbyDoc.First();
                                actualfilename = string.Format("{0}_Page_{1}{2}", pagedetails.FolderName, pagedetails.TotalPageCount, pagedetails.FileType);
                                if (pagesbyDoc.Any() )
                                {
                                    //TODO: FIND SECTION TAG - LOGIC TODO


                                    //STITCHING PDF                                   
                                    MemoryStream docStream = pagedetails.FileType.ToLower().Contains("pdf") ? docMigrationPDFStitcher.MergePDFs(pagesbyDoc, baseRecordsLocation) : docMigrationPDFStitcher.MergeImages(pagesbyDoc);


                                    if (docStream != null)
                                    {

                                        using (MemoryStream stitchedFileStream = OCRTOPdf.ConvertToSearchablePDF(docStream))
                                        {
                                            var destinationfilename_guidbased = string.Format("{0}{1}", Guid.NewGuid().ToString(), pagedetails.FileType);
                                            var s3filesubpath = string.Format("{0}/{1}", SystemSettings.MinistryRecordsBucket, _requestnumber.ToUpper());

                                            var uploadresponse = await docMigrationS3Client.UploadFileAsync(new UploadFile() { AXISRequestID = _requestnumber.ToUpper(), SubFolderPath = s3filesubpath, DestinationFileName = destinationfilename_guidbased, FileStream = stitchedFileStream });

                                            if (uploadresponse != null && uploadresponse.IsSuccessStatusCode)
                                            {



                                                int.TryParse(pagedetails.TotalPageCount, out int pagecount);
                                                var documenthash = Guid.NewGuid().ToString().Replace("-", "");
                                                var batch = Guid.NewGuid().ToString();
                                                var s3url = string.Format("{0}/{1}/{2}", SystemSettings.S3_EndPoint, s3filesubpath, destinationfilename_guidbased);
                                                byte[] fileData = stitchedFileStream.ToArray();
                                                int filesize = fileData.Length; //TODO: Need to find out the  KB or B or MB in DB
                                                var sectiondivisionid = 422;

                                                var minitryrequestdetails = recordsDAL.GetMinistryRequestDetails(_requestnumber);

                                                if (minitryrequestdetails.Item1 > -1)
                                                {

                                                    string attributesJSONtemplate = @"{{""divisions"": [{{""divisionid"": {0}}}], ""lastmodified"": ""{1}"", ""filesize"": {2}, ""batch"": ""{3}"", ""extension"": "".pdf"", ""incompatible"": false}}";
                                                    var attributedJSON = string.Format(attributesJSONtemplate, sectiondivisionid, DateTime.Now.ToString("MM-dd-yyy"), filesize, batch);

                                                    var recordid = recordsDAL.InsertIntoFOIRequestRecords(_requestnumber, s3url, actualfilename, attributedJSON, minitryrequestdetails.Item1, minitryrequestdetails.Item2);

                                                    if (recordid > -1)
                                                    {

                                                        var documentmasterid = recordsDAL.InsertIntoDocumentMaster(minitryrequestdetails.Item1, s3url, recordid);
                                                        var documentid = recordsDAL.InsertIntoDocuments(minitryrequestdetails.Item1, actualfilename, pagecount, documentmasterid);
                                                        var resultAttributes = recordsDAL.InsertIntoDocumentAttributes(documentmasterid, attributedJSON);
                                                        var resultInsertIntoDocumentHashcodes = recordsDAL.InsertIntoDocumentHashcodes(documentid, documenthash);
                                                        var resultDedupljob = recordsDAL.InsertIntoDeduplicationJob(documentmasterid, minitryrequestdetails.Item1, batch, actualfilename);
                                                    }

                                                }
                                                else
                                                {
                                                    ilogger.LogError(string.Format("Ministry Request ID not found for Request Number {0}",_requestnumber));
                                                }

                                            }

                                        }
                                    }

                                }
                            }
                            catch (Exception ex)
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
