using Amazon.Runtime.Internal.Util;
using Amazon.S3;
using MCS.FOI.AXISIntegration.DAL;
using MCS.FOI.AXISIntegration.DAL.Interfaces;
using MCS.FOI.AXISIntegration.DataModels.Document;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Cors;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using MCS.FOI.AXISIntegration.Utilities.Types;
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace MCS.FOI.AXISIntegrationWebAPI.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [EnableCors(PolicyName = "FOIOrigins")]
    [Authorize]
    public class DocumentsSyncController : ControllerBase
    {

        private readonly ILogger<DocumentsSyncController> _logger;
        private readonly IRequestDA _requestDA;
        private readonly IFOIFlowRequestUserDA _fOIFlowRequestUser;
        private IAmazonS3 amazonS3;
        private readonly S3Configuration _s3Config;

        public DocumentsSyncController(
            ILogger<DocumentsSyncController> logger,
            IRequestDA requestDA,
            IFOIFlowRequestUserDA fOIFlowRequestUser,
            IAmazonS3 _amazonS3,
            IOptions<S3Configuration> s3Config)
        {
            _logger = logger;
            _requestDA = requestDA;
            _fOIFlowRequestUser = fOIFlowRequestUser;
            _s3Config = s3Config.Value;
            amazonS3 = _amazonS3;
        }

        [HttpPost]
        public async Task<ActionResult<string>> Post([FromBody] CorrespondenceRequest request)
        {
            try
            {
                DocMigrationS3Client docMigrationS3Client = new DocMigrationS3Client(amazonS3);

                foreach (AXISFile file in request.CorrespondenceLogs)
                {
                    try
                    {
                        if (file.CorrespondenceType == "upload" || file.CorrespondenceType == "attachment")
                        {
                            //NOT AN EMAIL UPLOAD - DIRECT FILE UPLOAD  - For e.g. https://citz-foi-prod.objectstore.gov.bc.ca/dev-forms-foirequests-e/Misc/CFD-2023-22081302/applicant/00b8ad71-5d11-4624-9c12-839193cf4a7e.docx
                            var UNCFileLocation = Path.Combine(_s3Config.FileServerRoot, _s3Config.CorrespondenceLogBaseFolder, file.FilePathOnServer.Trim());
                            //var UNCFileLocation = file.FileExtension == "pdf" ? @"\\DESKTOP-U67UC02\ioashare\db7e84e1-4202-4837-b4dd-49af233ae006.pdf" : @"\\DESKTOP-U67UC02\ioashare\DOCX1.docx";

                            using (FileStream fs = System.IO.File.Open(UNCFileLocation, FileMode.Open))
                            {
                                var s3filesubpath = string.Format("{0}/{1}/{2}", _s3Config.S3_Attachements_BasePath, file.AXISRequestID, _s3Config.AttachmentTag);
                                var destinationfilename = string.Format("{0}.{1}", Guid.NewGuid().ToString(), file.FileExtension);
                                var uploadresponse = await docMigrationS3Client.UploadFileAsync(new UploadFile() { AXISRequestID = file.AXISRequestID.ToUpper(), SubFolderPath = s3filesubpath, DestinationFileName = destinationfilename, FileStream = fs });
                                var fullfileurl = string.Format("{0}/{1}/{2}", _s3Config.AWS_S3_Url, s3filesubpath, destinationfilename);
                                if (uploadresponse.IsSuccessStatusCode)
                                {
                                    //INSERT INTO TABLE - FOIMinistryRequestDocuments
                                    _fOIFlowRequestUser.InsertIntoMinistryRequestDocuments(fullfileurl, FilePathUtils.CleanFileNameInput(file.FileName), file.AXISRequestID.ToUpper(), file.CorrespondenceID ?? 0, file.CorrespondenceType, request.UserId);
                                }
                            }
                        }
                        else
                        {
                            //Create EMAIL MSG PDF
                            DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher();
                            using (Stream emailmessagepdfstream = docMigrationPDFStitcher.CreatePDFDocument(file.EmailContent, file.EmailSubject, file.EmailDate, file.EmailTo, file.AttachmentName))
                            {
                                var s3filesubpath = string.Format("{0}/{1}/{2}", _s3Config.S3_Attachements_BasePath, file.AXISRequestID.ToUpper(), _s3Config.AttachmentTag);
                                var destinationfilename = string.Format("{0}.pdf", Guid.NewGuid().ToString());
                                var uploadresponse = await docMigrationS3Client.UploadFileAsync(new UploadFile() { AXISRequestID = file.AXISRequestID.ToUpper(), SubFolderPath = s3filesubpath, DestinationFileName = destinationfilename, FileStream = emailmessagepdfstream });
                                var fullfileurl = string.Format("{0}/{1}/{2}", _s3Config.AWS_S3_Url, s3filesubpath, destinationfilename);
                                if (uploadresponse.IsSuccessStatusCode)
                                {
                                    //INSERT INTO TABLE - FOIMinistryRequestDocuments
                                    _fOIFlowRequestUser.InsertIntoMinistryRequestDocuments(fullfileurl, string.Format("{0}.pdf", FilePathUtils.CleanFileNameInput(file.EmailSubject + "_" + file.CorrespondenceID)), file.AXISRequestID.ToUpper(), file.CorrespondenceID ?? 0, file.CorrespondenceType, request.UserId);
                                }
                            }
                        }
                    }
                    catch(Exception ex) 
                    {
                        _logger.LogError(string.Format("Error happened while uploading correspondence log for request : {0} and error is like, {1}", file.AXISRequestID.ToUpper(), ex.Message));
                        return BadRequest();
                    }
                }

                Console.WriteLine("Completed : AXIS Sync Correspondence logs.... ");
                return Ok("Success");
            }
            catch(Exception e) 
            {
                _logger.LogError(string.Format("Correspondence log sync, Error happened : {0}", e.Message));
                return BadRequest();
            }

        }
    }

   public class CorrespondenceRequest
    {
        public string UserId { get; set; }
        public List<AXISFile> CorrespondenceLogs { get; set; }
    }
}
