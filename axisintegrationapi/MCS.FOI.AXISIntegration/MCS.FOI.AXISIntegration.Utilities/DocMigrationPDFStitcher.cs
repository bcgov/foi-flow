using PdfSharpCore;
using PdfSharpCore.Pdf;
using PdfSharpCore.Pdf.IO;
using SyncfusionPDF = Syncfusion.Pdf;
using SyncfusionPDFGraphics = Syncfusion.Pdf.Graphics;
using TheArtOfDev.HtmlRenderer.PdfSharp;
using Syncfusion.Pdf.Graphics;
using Syncfusion.Drawing;
using Amazon.S3.Model;
using Syncfusion.Pdf.Parsing;

namespace MCS.FOI.AXISIntegration.Utilities
{
    public class DocMigrationPDFStitcher : IDisposable
    {
        private Stream createemailpdfmemorystream = null;
        public DocMigrationPDFStitcher()
        {

        }

        public void Dispose()
        {

            createemailpdfmemorystream?.Close();
            createemailpdfmemorystream?.Dispose();
        }

        public Stream CreatePDFDocument(string emailcontent, string emailsubject, string emaildate, string emailTo, string attachementfilename = null)
        {
            try
            {
                string attachment = string.Empty;
                if (attachementfilename != null) { attachment = attachementfilename; }

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
			                            <td>Attachment</td>
			                            <td>{3}</td>
		                            </tr>
		                            <tr>
			                            <td>Message</td>
			                            <td>{4}</td>
		                            </tr>
	                            </tbody>
                            </table>", emailTo, emaildate, emailsubject, attachment, emailcontent);

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
