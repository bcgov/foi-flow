namespace SyncfusionDocument.Controllers
{
    [Route("api/[controller]")]
    [EnableCors(PolicyName = "FOIOrigins")]
    [Authorize(Policy = "IAOTeam")]
    public class DocumentEditorController : Controller
    {
        [HttpPost]
        [Route("SpellCheck")]
        [AllowAnonymous]
        public string SpellCheck([FromBody] SpellCheckJsonData spellChecker)
        {
            try
            {
                // Create SpellChecker instance
                SpellChecker spellCheck = new SpellChecker();

                if (spellChecker.AddWord)
                {
                    return Newtonsoft.Json.JsonConvert.SerializeObject(spellCheck);
                }

                // Perform Spell Check
                spellCheck.GetSuggestions(spellChecker.LanguageID, spellChecker.TexttoCheck,
                                          spellChecker.CheckSpelling, spellChecker.CheckSuggestion,
                                          spellChecker.AddWord);

                return Newtonsoft.Json.JsonConvert.SerializeObject(spellCheck);
            }
            catch (Exception ex)
            {
                Console.WriteLine("SpellCheck Error: " + ex.Message);
                return "{\"SpellCollection\":[],\"HasSpellingError\":false,\"Suggestions\":null}";
            }
        }

        [AcceptVerbs("Post")]
        [HttpPost]
        [Route("SpellCheckByPage")]
        [AllowAnonymous]
        public string SpellCheckByPage([FromBody] SpellCheckJsonData spellChecker)
        {
            try
            {
                SpellChecker spellCheck = new SpellChecker();
                spellCheck.CheckSpelling(spellChecker.LanguageID, spellChecker.TexttoCheck);
                return Newtonsoft.Json.JsonConvert.SerializeObject(spellCheck);
            }
            catch
            {
                return "{\"SpellCollection\":[],\"HasSpellingError\":false,\"Suggestions\":null}";
            }
        }

        [AcceptVerbs("Post")]
        [HttpPost]
        [Route("ExportSFDT")]
        public FileStreamResult ExportSFDT([FromBody] SaveParameter data)
        {
            string name = data.FileName;
            string format = DocumentEditorHelper.RetrieveFileType(name);
            if (string.IsNullOrEmpty(name))
            {
                name = "Document1.doc";
            }
            WDocument document = WordDocument.Save(data.Content);
            return DocumentEditorHelper.SaveDocument(document, format, name);
        }

        [AcceptVerbs("Post")]
        [HttpPost]
        [Route("ExportPdf")]
        public FileStreamResult ExportPdf([FromBody] SaveParameter data)
        {
            // Converts the sfdt to stream
            Stream document = WordDocument.Save(data.Content, FormatType.Docx);
            document.Position = 0;
            Syncfusion.DocIO.DLS.WordDocument doc = new Syncfusion.DocIO.DLS.WordDocument(document, Syncfusion.DocIO.FormatType.Automatic);
            //Instantiation of DocIORenderer for Word to PDF conversion 
            DocIORenderer render = new DocIORenderer();
            //Converts Word document into PDF document 
            PdfDocument pdfDocument = render.ConvertToPDF(doc);
            Stream stream = new MemoryStream();

            //Saves the PDF file
            pdfDocument.Save(stream);
            stream.Position = 0;
            pdfDocument.Close();
            document.Close();
            return new FileStreamResult(stream, "application/pdf")
            {
                FileDownloadName = data.FileName
            };
        }

        #region Document Editor Functionality that might be usable
        //private readonly IWebHostEnvironment _hostingEnvironment;
        //private readonly IConfiguration _configuration;
        //string path;

        //public DocumentEditorController(IWebHostEnvironment hostingEnvironment, IConfiguration configuration)
        //{
        //    _hostingEnvironment = hostingEnvironment;
        //    _configuration = configuration;
        //    path = configuration.GetValue<string>("SPELLCHECK_DICTIONARY_PATH") ?? string.Empty;
        //}

        //[AcceptVerbs("Post")]
        //[HttpPost]
        //[Route("Import")]
        //public string Import(IFormCollection data)
        //{
        //    if (data.Files.Count == 0)
        //        return null;
        //    Stream stream = new MemoryStream();
        //    IFormFile file = data.Files[0];
        //    int index = file.FileName.LastIndexOf('.');
        //    string type = index > -1 && index < file.FileName.Length - 1 ?
        //        file.FileName.Substring(index) : ".docx";
        //    file.CopyTo(stream);
        //    stream.Position = 0;

        //    //Hooks MetafileImageParsed event.
        //    WordDocument.MetafileImageParsed += DocumentEditorHelper.OnMetafileImageParsed;
        //    WordDocument document = WordDocument.Load(stream, DocumentEditorHelper.GetFormatType(type.ToLower()));
        //    //Unhooks MetafileImageParsed event.
        //    WordDocument.MetafileImageParsed -= DocumentEditorHelper.OnMetafileImageParsed;

        //    string json = Newtonsoft.Json.JsonConvert.SerializeObject(document);
        //    document.Dispose();
        //    return json;
        //}


        //[AcceptVerbs("Post")]
        //[HttpPost]
        //[Route("MailMerge")]
        //public string MailMerge([FromBody] ExportData exportData)
        //{
        //    Byte[] data = Convert.FromBase64String(exportData.documentData.Split(',')[1]);
        //    MemoryStream stream = new MemoryStream();
        //    stream.Write(data, 0, data.Length);
        //    stream.Position = 0;
        //    try
        //    {
        //        Syncfusion.DocIO.DLS.WordDocument document = new Syncfusion.DocIO.DLS.WordDocument(stream, Syncfusion.DocIO.FormatType.Docx);
        //        document.MailMerge.RemoveEmptyGroup = true;
        //        document.MailMerge.RemoveEmptyParagraphs = true;
        //        document.MailMerge.ClearFields = true;
        //        document.MailMerge.Execute(new List<object>());
        //        document.Save(stream, Syncfusion.DocIO.FormatType.Docx);
        //    }
        //    catch (Exception ex)
        //    {
        //        return ex.Message;
        //    }
        //    string sfdtText = "";
        //    Syncfusion.EJ2.DocumentEditor.WordDocument document1 = Syncfusion.EJ2.DocumentEditor.WordDocument.Load(stream, Syncfusion.EJ2.DocumentEditor.FormatType.Docx);
        //    sfdtText = Newtonsoft.Json.JsonConvert.SerializeObject(document1);
        //    document1.Dispose();
        //    return sfdtText;
        //}

        [AcceptVerbs("Post")]
        [HttpPost]
        [EnableCors("AllowAllOrigins")]
        [AllowAnonymous]
        [Route("SystemClipboard")]
        public string SystemClipboard([FromBody] CustomParameter param)
        {
           if (param.content != null && param.content != "")
           {
               try
               {
                   //Hooks MetafileImageParsed event.
                   WordDocument.MetafileImageParsed += DocumentEditorHelper.OnMetafileImageParsed;
                   WordDocument document = WordDocument.LoadString(param.content, DocumentEditorHelper.GetFormatType(param.type.ToLower()));
                   //Unhooks MetafileImageParsed event.
                   WordDocument.MetafileImageParsed -= DocumentEditorHelper.OnMetafileImageParsed;
                   string json = Newtonsoft.Json.JsonConvert.SerializeObject(document);
                   document.Dispose();
                   return json;
               }
               catch (Exception)
               {
                   return "";
               }
           }
           return "";
        }

        //[AcceptVerbs("Post")]
        //[HttpPost]
        //[Route("RestrictEditing")]
        //public string[] RestrictEditing([FromBody] CustomRestrictParameter param)
        //{
        //    if (param.passwordBase64 == "" && param.passwordBase64 == null)
        //        return null;
        //    return WordDocument.ComputeHash(param.passwordBase64, param.saltBase64, param.spinCount);
        //}

        //[AcceptVerbs("Post")]
        //[HttpPost]
        //[Route("LoadDefault")]
        //public string LoadDefault()
        //{
        //    Stream stream = System.IO.File.OpenRead("App_Data/GettingStarted.docx");
        //    stream.Position = 0;

        //    WordDocument document = WordDocument.Load(stream, FormatType.Docx);
        //    string json = Newtonsoft.Json.JsonConvert.SerializeObject(document);
        //    document.Dispose();
        //    return json;
        //}

        //[AcceptVerbs("Post")]
        //[HttpPost]
        //[Route("LoadDocument")]
        //public string LoadDocument([FromForm] UploadDocument uploadDocument)
        //{
        //    string documentPath = Path.Combine(path, uploadDocument.DocumentName);
        //    Stream stream = null;
        //    if (System.IO.File.Exists(documentPath))
        //    {
        //        byte[] bytes = System.IO.File.ReadAllBytes(documentPath);
        //        stream = new MemoryStream(bytes);
        //    }
        //    else
        //    {
        //        bool result = Uri.TryCreate(uploadDocument.DocumentName, UriKind.Absolute, out Uri uriResult)
        //            && (uriResult.Scheme == Uri.UriSchemeHttp || uriResult.Scheme == Uri.UriSchemeHttps);
        //        if (result)
        //        {
        //            stream = GetDocumentFromURL(uploadDocument.DocumentName).Result;
        //            if (stream != null)
        //                stream.Position = 0;
        //        }
        //    }
        //    WordDocument document = WordDocument.Load(stream, FormatType.Docx);
        //    string json = Newtonsoft.Json.JsonConvert.SerializeObject(document);
        //    document.Dispose();
        //    return json;
        //}

        //async Task<MemoryStream> GetDocumentFromURL(string url)
        //{
        //    var client = new HttpClient(); ;
        //    var response = await client.GetAsync(url);
        //    var rawStream = await response.Content.ReadAsStreamAsync();
        //    if (response.IsSuccessStatusCode)
        //    {
        //        MemoryStream docStream = new MemoryStream();
        //        rawStream.CopyTo(docStream);
        //        return docStream;
        //    }
        //    else { return null; }
        //}

        //[AcceptVerbs("Post")]
        //[HttpPost]
        //[Route("Save")]
        //public void Save([FromBody] SaveParameter data)
        //{
        //    string name = data.FileName;
        //    string format = DocumentEditorHelper.RetrieveFileType(name);
        //    if (string.IsNullOrEmpty(name))
        //    {
        //        name = "Document1.doc";
        //    }
        //    WDocument document = WordDocument.Save(data.Content);
        //    FileStream fileStream = new FileStream(name, FileMode.OpenOrCreate, FileAccess.ReadWrite);
        //    document.Save(fileStream, DocumentEditorHelper.GetWFormatType(format));
        //    document.Close();
        //    fileStream.Close();
        //}


        //[AcceptVerbs("Post")]
        //[HttpPost]
        //[Route("Export")]
        //public FileStreamResult Export(IFormCollection data)
        //{
        //    if (data.Files.Count == 0)
        //        return null;
        //    string fileName = DocumentEditorHelper.GetValue(data, "filename");
        //    string name = fileName;
        //    string format = DocumentEditorHelper.RetrieveFileType(name);
        //    if (string.IsNullOrEmpty(name))
        //    {
        //        name = "Document1";
        //    }
        //    WDocument document = DocumentEditorHelper.GetDocument(data);
        //    return DocumentEditorHelper.SaveDocument(document, format, fileName);
        //}
        #endregion
    }
}
