using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Amazon;
using FOIMOD.CFD.DocMigration.Models.Document;
using PdfSharpCore;
using PdfSharpCore.Pdf;
using PdfSharpCore.Pdf.IO;

namespace FOIMOD.CFD.DocMigration.Utils
{
    public class DocMigrationPDFStitcher :IDisposable
    {
        
        private  Stream mergeddocstream = null;
        public DocMigrationPDFStitcher()
        {
           
        }

        public void Dispose()
        {
            
            mergeddocstream.Close();
            mergeddocstream.Dispose();
        }

        public Stream  MergePDFs(PDFDocToMerge[] pdfpages)
        {
            var _pdfpages = pdfpages.OrderBy(p => p.PageSequenceNumber).ToArray<PDFDocToMerge>();
            using (PdfDocument pdfdocument = new PdfDocument())
            {
                foreach (PDFDocToMerge pDFDocToMerge in _pdfpages)
                {
                    using PdfDocument inputPDFDocument = PdfReader.Open(pDFDocToMerge.PageFilePath, PdfDocumentOpenMode.Import);
                    pdfdocument.Version = inputPDFDocument.Version;
                    foreach (PdfPage page in inputPDFDocument.Pages)
                    {
                        pdfdocument.AddPage(page);
                    }
                }
                mergeddocstream = new MemoryStream();
                pdfdocument.Save(mergeddocstream);
            }
            return mergeddocstream;
        }
    }
}
