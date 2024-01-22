
using Syncfusion.OCRProcessor;
using Syncfusion.Pdf.Parsing;
using System.Runtime.CompilerServices;

namespace MCS.FOI.OCRtoPDF
{
    public  static class OCRTOPdf
    {
        public static string TessaractPath { get; set; }
        public static string TessaractLanguagePath { get; set; }

        public static MemoryStream ConvertToSearchablePDF(FileStream inputPdfFilestream)
        {
            
            using (OCRProcessor processor = new OCRProcessor(TessaractPath))
            {
                using FileStream fileStream = inputPdfFilestream;
                //Load a PDF document.
                using PdfLoadedDocument lDoc = new PdfLoadedDocument(fileStream);
                //Set OCR language to process.
                processor.Settings.Language = Languages.English;
                //Process OCR by providing the PDF document.
                processor.PerformOCR(lDoc,TessaractLanguagePath);


                //Create memory stream.
                MemoryStream stream = new MemoryStream();
                //Save the document to memory stream.
                lDoc.Save(stream);
                lDoc.Close();
                //Set the position as '0'.
                stream.Position = 0;
                return stream;
               
            }

        }

    }
}
