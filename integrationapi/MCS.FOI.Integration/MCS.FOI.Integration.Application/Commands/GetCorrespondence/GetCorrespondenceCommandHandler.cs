using MCS.FOI.Integration.Core.Repositories.RedisRepository;

namespace MCS.FOI.Integration.Application.Commands.GetCorrespondence
{
    public class GetCorrespondenceCommandHandler : ICommandHandler<GetCorrespondenceCommand, string>
    {
        private readonly ITemplateMappingService _templateMapping;
        private readonly IS3ConnectionService _s3StorageService;
        private readonly ITemplateRepository _templateRepository;
        private readonly ITemplateRedisCacheRepository _templateCacheService;

        public GetCorrespondenceCommandHandler(
            ITemplateMappingService templateMapping,
            IS3ConnectionService s3StorageService,
            ITemplateRepository templateRepository,
            ITemplateRedisCacheRepository templateCacheService)
        {
            _templateMapping = templateMapping;
            _s3StorageService = s3StorageService;
            _templateRepository = templateRepository;
            _templateCacheService = templateCacheService;
        }

        public async Task<string> Handle(GetCorrespondenceCommand command, CancellationToken cancellationToken = default)
        {
            var template = await GetTemplateAsync(command.FileName);
            if (template == null || string.IsNullOrWhiteSpace(template.DocumentPath))
                throw new NotFoundException($"Template not found for filename: {command.FileName}");

            var templateCache = await _templateCacheService.GetTemplateCacheAsync(command.FileName);
            string base64DocumentString = templateCache?.EncodedContent ?? string.Empty;

            if (templateCache == null || string.IsNullOrEmpty(templateCache?.EncodedContent))
            {
                var documentFiles = await _s3StorageService.FetchTemplatesAsync(command.FileName, command.Token, template.DocumentPath, cancellationToken);
                base64DocumentString = documentFiles?.FirstOrDefault()?.Text ?? string.Empty;
                template.EncodedContent = base64DocumentString;
                await _templateCacheService.SetTemplateCacheAsync(template);
            }

            var fileBytes = DecodeBase64File(base64DocumentString);

            if (template.Extension.Equals($".{FormatType.Docx}", StringComparison.OrdinalIgnoreCase))
                ValidateDocumentStructure(fileBytes);

            using var document = LoadWordDocument(fileBytes, template.Extension);

            var templateData = await _templateMapping.GenerateFieldsMapping(command.FOIRequestId, command.FOIMinistryRequestId);
            ReplacePlaceholders(document, templateData);

            using var outputStream = new MemoryStream();
            document.Save(outputStream, FormatType.Docx);
            outputStream.Position = 0;

            var sfdt = ConvertToSfdt(outputStream);
           
            return sfdt;
        }

        #region Template Retrieval
        private async Task<TemplateDto> GetTemplateAsync(string fileName)
        {
            var template = await _templateRepository.GetAsync(r => r.IsActive && r.FileName.Equals(fileName));
            return IMap.Mapper.Map<TemplateDto>(template?.FirstOrDefault());
        }
        #endregion

        #region Validation 
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

        private static WordDocument LoadWordDocument(byte[] fileBytes, string extension)
        {
            var fileStream = new MemoryStream(fileBytes);
            return new WordDocument(fileStream, GetDocIOFormatType(extension));
        }

        #endregion

        #region Field Mapping
        private void ReplacePlaceholders(WordDocument document, IEnumerable<TemplateFieldMappingDto> templateData)
        {
            foreach (var field in templateData)
            {
                if (!string.IsNullOrEmpty(field.FieldValue))
                {
                    // Check if the value contains HTML content (a simple check for "<p>" or "<div>")
                    if (field.FieldValue.Contains("<p>") || field.FieldValue.Contains("<div>") || field.FieldValue.Contains("<table>"))
                    {
                        ReplacePlaceholderWithHtml(document, field.FieldName, field.FieldValue);
                    }
                    else
                    {
                        ReplacePlaceholder(document, field.FieldName, field.FieldValue);
                    }
                }
            }
        }

        private void ReplacePlaceholder(WordDocument document, string placeholder, string replacement)
        {
            TextSelection selection;
            // Continue replacing until no more instances are found.
            while ((selection = document.Find(placeholder, false, true)) != null)
            {
                var textRange = selection.GetAsOneRange();
                textRange.Text = replacement ?? string.Empty;
            }
        }

        private void ReplacePlaceholderWithHtml(WordDocument document, string placeholder, string htmlContent)
        {
            TextSelection selection;
            while ((selection = document.Find(placeholder, false, true)) != null)
            {
                var textRange = selection.GetAsOneRange();

                // Create a temporary document for HTML content
                WordDocument tempDoc = new WordDocument();
                IWSection section = tempDoc.AddSection();
                IWParagraph paragraph = section.AddParagraph();

                // Append HTML content to the paragraph
                paragraph.AppendHTML(htmlContent);

                // Import the section into the main document
                foreach (IWSection sec in tempDoc.Sections)
                {
                    document.Sections.Add(sec.Clone());
                }

                // Remove the placeholder
                textRange.Text = string.Empty;
            }
        }
        #endregion

        #region Conversion
        private string ConvertToSfdt(MemoryStream stream)
        {
            stream.Position = 0;
            var documentEditor = Syncfusion.EJ2.DocumentEditor.WordDocument.Load(stream, GetFormatType(".docx"));
            return JsonConvert.SerializeObject(documentEditor);
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

        private static Syncfusion.DocIO.FormatType GetDocIOFormatType(string format)
        {
            return format.ToLower() switch
            {
                ".dotx" or ".docx" or ".docm" or ".dotm" => Syncfusion.DocIO.FormatType.Docx,
                ".dot" or ".doc" => FormatType.Doc,
                ".rtf" => Syncfusion.DocIO.FormatType.Rtf,
                ".txt" => Syncfusion.DocIO.FormatType.Txt,
                ".xml" => Syncfusion.DocIO.FormatType.WordML,
                ".html" => Syncfusion.DocIO.FormatType.Html,
                _ => throw new NotSupportedException("Syncfusion.DocIO does not support this file format.")
            };
        }
        #endregion
    }
}
