namespace MCS.FOI.Integration.Application.Commands.GetCorrespondence
{
    public class GetCorrespondenceCommandHandler : ICommandHandler<GetCorrespondenceCommand, string>
    {
        private readonly IWebHostEnvironment _hostingEnvironment; // to be removedd
        private readonly ITemplateMappingService _templateMapping;
        private readonly IS3ConnectionService _s3StorageService;
        private readonly ITemplateRepository _templateRepository;

        public GetCorrespondenceCommandHandler(
            IWebHostEnvironment hostingEnvironment,
            ITemplateMappingService templateMapping,
            IS3ConnectionService s3StorageService,
            ITemplateRepository templateRepository)
        {
            _hostingEnvironment = hostingEnvironment;
            _templateMapping = templateMapping;
            _s3StorageService = s3StorageService;
            _templateRepository = templateRepository;
        }

        public async Task<string> Handle(GetCorrespondenceCommand command, CancellationToken cancellationToken = default)
        {
            var templatePath = await GetTemplatePathAsync(command.FileName);
            if (string.IsNullOrEmpty(templatePath))
                throw new NotFoundException($"Template not found for filename: {command.FileName}");

            var documentFiles = await _s3StorageService.FetchTemplatesAsync(command, templatePath, cancellationToken);
            var templateData = await _templateMapping.GenerateFieldsMapping(command.FOIRequestId, command.FOIMinistryRequestId);

            var base64Document = documentFiles?.FirstOrDefault()?.Text;
            var fileBytes = DecodeBase64File(base64Document);
            ValidateDocumentStructure(fileBytes);

            using var document = LoadWordDocument(fileBytes);

            ReplacePlaceholders(document, templateData);

            using var outputStream = new MemoryStream();
            document.Save(outputStream, FormatType.Docx);
            outputStream.Position = 0;

            return ProcessGeneratedDocument(outputStream, command);
        }

        #region Validation 
        private async Task<string> GetTemplatePathAsync(string fileName)
        {
            var template = await _templateRepository.GetAsync(r => r.IsActive && r.FileName.Equals(fileName));
            return template?.FirstOrDefault()?.DocumentPath ?? string.Empty;
        }

        private static byte[] DecodeBase64File(string base64Text)
        {
            try
            {
                var fileBytes = Convert.FromBase64String(base64Text);
                if (fileBytes.Length == 0)
                {
                    throw new NotValidOperationException("Decoded file bytes are empty.");
                }
                return fileBytes;
            }
            catch (FormatException ex)
            {
                throw new NotValidOperationException("Invalid Base64 encoding in the document file.");
            }
        }

        private static void ValidateDocumentStructure(byte[] fileBytes)
        {
            ValidateZipStructure(fileBytes);
            ValidateWordDocument(fileBytes);
        }

        private static void ValidateZipStructure(byte[] fileBytes)
        {
            using var tempStream = new MemoryStream(fileBytes);
            try
            {
                using var zipArchive = new ZipArchive(tempStream, ZipArchiveMode.Read);
            }
            catch (InvalidDataException)
            {
                throw new NotValidOperationException("The provided file is not a valid DOCX (ZIP archive structure is missing or corrupted).");
            }
        }

        private static void ValidateWordDocument(byte[] fileBytes)
        {
            using var fileStream = new MemoryStream(fileBytes);
            try
            {
                using var document = new WordDocument(fileStream, FormatType.Docx)
                {
                };
            }
            catch (Exception ex)
            {
                throw new NotValidOperationException("The provided file is not a valid DOCX.");
            }
        }

        private static WordDocument LoadWordDocument(byte[] fileBytes)
        {
            var fileStream = new MemoryStream(fileBytes);
            return new WordDocument(fileStream, FormatType.Docx);
        }

        #endregion

        #region Field Mapping
        private void ReplacePlaceholders(WordDocument document, IEnumerable<TemplateFieldMappingDto> templateData)
        {
            foreach (var field in templateData)
            {
                ReplacePlaceholder(document, field.FieldName, field.FieldValue);
            }
        }

        private void ReplacePlaceholder(WordDocument document, string placeholder, string replacement)
        {
            TextSelection selection;
            // Continue replacing until no more instances are found.
            while ((selection = document.Find(placeholder, false, true)) != null)
            {
                var textRange = selection.GetAsOneRange();
                textRange.Text = replacement;
            }
        }

        #endregion

        #region Conversion
        private string ProcessGeneratedDocument(MemoryStream stream, GetCorrespondenceCommand command)
        {
            var sfdt = ConvertToSfdt(stream);
            SaveToFile(stream, "GeneratedDocuments", $"{DateTime.Now:MMMM dd, yyyy}-{command.FileName}.docx");
            return sfdt;
        }

        private string ConvertToSfdt(MemoryStream stream)
        {
            stream.Position = 0;
            var documentEditor = Syncfusion.EJ2.DocumentEditor.WordDocument.Load(stream, GetFormatType(".docx"));
            return JsonConvert.SerializeObject(documentEditor);
        }

        //to be removed - for debugging purpose only
        private void SaveToFile(Stream stream, string folder, string fileName)
        {
            var outputPath = Path.Combine(_hostingEnvironment.ContentRootPath, folder, fileName);
            Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);

            stream.Position = 0;
            using var outputFileStream = new FileStream(outputPath, FileMode.Create, FileAccess.Write);
            stream.CopyTo(outputFileStream);
        }

        private static Syncfusion.EJ2.DocumentEditor.FormatType GetFormatType(string format)
        {
            return format.ToLower() switch
            {
                ".dotx" or ".docx" or ".docm" or ".dotm" => Syncfusion.EJ2.DocumentEditor.FormatType.Docx,
                ".dot" or ".doc" => Syncfusion.EJ2.DocumentEditor.FormatType.Doc,
                ".rtf" => Syncfusion.EJ2.DocumentEditor.FormatType.Rtf,
                ".txt" => Syncfusion.EJ2.DocumentEditor.FormatType.Txt,
                ".xml" => Syncfusion.EJ2.DocumentEditor.FormatType.WordML,
                _ => throw new NotSupportedException("EJ2 DocumentEditor does not support this file format.")
            };
        }
        #endregion
    }
}
