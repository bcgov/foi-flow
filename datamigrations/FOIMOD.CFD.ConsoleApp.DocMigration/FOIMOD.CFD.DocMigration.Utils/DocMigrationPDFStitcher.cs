using FOIMOD.CFD.DocMigration.Models;
using FOIMOD.CFD.DocMigration.Models.Document;
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




namespace FOIMOD.CFD.DocMigration.Utils
{
    public class DocMigrationPDFStitcher : IDisposable
    {

        private MemoryStream mergeddocstream = null;
        private Stream createemailpdfmemorystream = null;
        public DocMigrationPDFStitcher()
        {

        }

        public void Dispose()
        {

            mergeddocstream.Close();
            mergeddocstream.Dispose();
        }

        public MemoryStream MergePDFs(List<DocumentToMigrate> pdfpages, string baseUNClocation = null)
        {
            var _pdfpages = pdfpages.OrderBy(p => p.PageSequenceNumber).ToArray<DocumentToMigrate>();
            using (PdfDocument pdfdocument = new PdfDocument())
            {
                foreach (DocumentToMigrate pDFDocToMerge in _pdfpages)
                {
                    string filelocation = String.IsNullOrEmpty(baseUNClocation) ? pDFDocToMerge.PageFilePath : Path.Combine(baseUNClocation, pDFDocToMerge.SiFolderID, pDFDocToMerge.PageFilePath);
                    using PdfDocument inputPDFDocument = !pDFDocToMerge.HasStreamForDocument ? PdfReader.Open(filelocation, PdfDocumentOpenMode.Import) : PdfReader.Open(pDFDocToMerge.FileStream, PdfDocumentOpenMode.Import);

                    pdfdocument.Version = inputPDFDocument.Version;

                    foreach (PdfPage page in inputPDFDocument.Pages)
                    {
                        pdfdocument.AddPage(page);
                    }
                }
                mergeddocstream = new MemoryStream();
                pdfdocument.Save(mergeddocstream);
                mergeddocstream.Position = 0;
            }
            return mergeddocstream;
        }

        public MemoryStream MergePDFs_v1(List<DocumentToMigrate> pdfpages, string baseUNClocation = null)
        {
            var _pdfpages = pdfpages.OrderBy(p => p.PageSequenceNumber).ToArray<DocumentToMigrate>();
            using (SyncfusionPDF.PdfDocument pdfdocument = new SyncfusionPDF.PdfDocument())
            {
                pdfdocument.PageSettings.Size = new SizeF(1500, 800);
                Stream[] streams = new Stream[_pdfpages.Length];
                int _inx = 0;

                foreach (DocumentToMigrate pDFDocToMerge in _pdfpages)
                {
                    string filelocation = String.IsNullOrEmpty(baseUNClocation) ? pDFDocToMerge.PageFilePath : Path.Combine(baseUNClocation, pDFDocToMerge.SiFolderID, pDFDocToMerge.PageFilePath);

                    streams[_inx] = new FileStream(filelocation, FileMode.Open, FileAccess.Read);
                    _inx++;

                }

                SyncfusionPDF.PdfDocumentBase.Merge(pdfdocument, streams);

                mergeddocstream = new MemoryStream();
                pdfdocument.Save(mergeddocstream);
                mergeddocstream.Position = 0;
            }
            return mergeddocstream;
        }

        public MemoryStream MergeImages(List<DocumentToMigrate> imagefiles, string baseUNClocation = null)
        {
            var _images = imagefiles.OrderBy(p => p.PageSequenceNumber).ToArray<DocumentToMigrate>();
            //Creating the new PDF document
            using SyncfusionPDF.PdfDocument document = new SyncfusionPDF.PdfDocument();

            foreach (var formFile in _images)
            {
                if (formFile.FileStream?.Length > 0)
                {
                    using MemoryStream file = new MemoryStream();
                    formFile.FileStream.CopyTo(file);
                    //Loading the image
                    //SyncfusionPDFGraphics.PdfImage image = SyncfusionPDFGraphics.PdfImage.FromStream(file);
                    PdfBitmap image = new PdfBitmap(file);
                    //Adding new page
                    SyncfusionPDF.PdfPage page = page = document.Pages.Add();

                    SizeF pageSize = page.GetClientSize();

                    //Setting image bounds 
                    RectangleF imageBounds = new RectangleF(0, 0, pageSize.Width, pageSize.Height);


                    //Drawing image to the PDF page
                    page.Graphics.DrawImage(image, imageBounds);
                    file.Dispose();
                }
                else
                {
                    using MemoryStream file = new MemoryStream();
                    string filelocation = String.IsNullOrEmpty(baseUNClocation) ? formFile.PageFilePath : Path.Combine(baseUNClocation, formFile.SiFolderID, formFile.PageFilePath);
                    //Adding new page
                    SyncfusionPDF.PdfPage page = page = document.Pages.Add();
                    if (formFile.FileType.Contains("pdf"))
                    {
                        using FileStream pdffilestream = File.OpenRead(filelocation);
                        //Loads the PDF document 
                        PdfLoadedDocument loadedDocument = new PdfLoadedDocument(pdffilestream);
                        //Set EnableMemoryOptimization to true
                        document.EnableMemoryOptimization = true;

                        //Appending the document with source document 
                        document.Append(loadedDocument);

                        //Close the loaded document
                        loadedDocument.Close(true);
                    }
                    else
                    {
                        PdfBitmap image = new PdfBitmap(File.Open(filelocation, FileMode.Open));
                        

                        SizeF pageSize = page.GetClientSize();

                        //Setting image bounds 
                        RectangleF imageBounds = new RectangleF(0, 0, pageSize.Width, pageSize.Height);


                        //Drawing image to the PDF page
                        page.Graphics.DrawImage(image, imageBounds);
                        file.Dispose();
                    }
                }

            }
            //Saving the PDF to the MemoryStream
            MemoryStream stream = new MemoryStream();

            document.Save(stream);

            //Set the position as '0'.
            stream.Position = 0;


            return stream;

        }


        public Stream CreatePDFDocument(string emailcontent, string emailsubject, string emaildate, string emailTo, List<AXISFIle> attachementfiles = null)
        {
            try
            {
                string attachmentlist = string.Empty;
                if (attachementfiles != null)
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
                            </table>", emailTo, emaildate, emailsubject, attachmentlist, emailcontent);

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
