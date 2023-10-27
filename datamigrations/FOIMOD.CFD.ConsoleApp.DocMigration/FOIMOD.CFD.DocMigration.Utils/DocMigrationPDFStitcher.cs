using FOIMOD.CFD.DocMigration.Models;
using FOIMOD.CFD.DocMigration.Models.Document;
using PdfSharpCore;
using PdfSharpCore.Pdf;
using PdfSharpCore.Pdf.IO;
using TheArtOfDev.HtmlRenderer.PdfSharp;

namespace FOIMOD.CFD.DocMigration.Utils
{
    public class DocMigrationPDFStitcher : IDisposable
    {

        private Stream mergeddocstream = null;
        private Stream createemailpdfmemorystream = null;
        public DocMigrationPDFStitcher()
        {

        }

        public void Dispose()
        {

            mergeddocstream.Close();
            mergeddocstream.Dispose();
        }

        public Stream MergePDFs(List<DocumentToMigrate> pdfpages)
        {
            var _pdfpages = pdfpages.OrderBy(p => p.PageSequenceNumber).ToArray<DocumentToMigrate>();
            using (PdfDocument pdfdocument = new PdfDocument())
            {
                foreach (DocumentToMigrate pDFDocToMerge in _pdfpages)
                {
                    using PdfDocument inputPDFDocument = !pDFDocToMerge.HasStreamForDocument ? PdfReader.Open(pDFDocToMerge.PageFilePath, PdfDocumentOpenMode.Import) : PdfReader.Open(pDFDocToMerge.FileStream, PdfDocumentOpenMode.Import);

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




        public Stream CreatePDFDocument(string emailcontent, string emailsubject, string emaildate, string emailTo,List<AXISFIle> attachementfiles)
        {
            try
            {
                string attachmentlist = string.Empty;
                if (attachementfiles!=null)
                {
                    attachmentlist += "<ul>";
                    foreach (var attachment in attachementfiles)
                    {
                        attachmentlist += string.Format("<li>{0}</li>", attachment.FileName);
                    }

                    attachmentlist += "</ul>";
                }

                var htmlofpdf = string.Format(@"<table border=""1"" cellpadding=""1"" cellspacing=""1"" style=""width:100%"">
	                            <tbody>
		                            <tr>
			                            <td>Emailed To</td>
			                            <td>{0}</td>
		                            </tr>
		                            <tr>
			                            <td>Date</td>
			                            <td>{1}</td>
		                            </tr>
		                            <tr>
			                            <td>Subject</td>
			                            <td>{2}</td>
		                            </tr>
                                    <tr>
			                            <td>Attachments</td>
			                            <td>
                                            {3}
                                         </td>
		                            </tr>
		                            <tr>
			                            <td>Message</td>
			                            <td>{4}</td>
		                            </tr>
	                            </tbody>
                            </table>", emailTo, emaildate, emailsubject, attachmentlist,emailcontent);

                using (PdfDocument pdfdocument = new PdfDocument())
                {
                    PdfGenerator.AddPdfPages(pdfdocument, htmlofpdf, PageSize.A4);
                    createemailpdfmemorystream = new MemoryStream();
                    pdfdocument.Save(createemailpdfmemorystream);
                }
            }
            catch (Exception ex)
            {
                createemailpdfmemorystream.Close();
                createemailpdfmemorystream.Dispose();
                Console.WriteLine(ex.Message);
                throw;
            }


            return createemailpdfmemorystream;

        }
    }
}
