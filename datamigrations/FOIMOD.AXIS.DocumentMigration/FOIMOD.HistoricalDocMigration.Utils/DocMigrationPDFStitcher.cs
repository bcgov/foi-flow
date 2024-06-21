using FOIMOD.HistoricalDocMigration.Models;
using FOIMOD.HistoricalDocMigration.Models.Document;
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




namespace FOIMOD.HistoricalDocMigration.Utils
{
    public class DocMigrationPDFStitcher : IDisposable
    {

        private HugeMemoryStream mergeddocstream = null;
        private Stream createemailpdfmemorystream = null;
        public DocMigrationPDFStitcher()
        {

        }

        public void Dispose()
        {

            mergeddocstream?.Close();
            mergeddocstream?.Dispose();
        }

        public HugeMemoryStream MergePDFs(List<DocumentToMigrate> pdfpages, string baseUNClocation = null)
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
                mergeddocstream = new HugeMemoryStream();
                pdfdocument.Save(mergeddocstream);
                mergeddocstream.Position = 0;
            }
            return mergeddocstream;
        }

        public MemoryStream MergePDFs_v2(List<DocumentToMigrate> pdfpages, string baseUNClocation = null)
        {
            MemoryStream stream = null;
            try
            {
                var _pdfpages = pdfpages.OrderBy(p => p.PageSequenceNumber).ToArray<DocumentToMigrate>();
                using SyncfusionPDF.PdfDocument document = new SyncfusionPDF.PdfDocument();
                foreach (DocumentToMigrate pDFDocToMerge in _pdfpages)
                {
                    using MemoryStream file = new MemoryStream();
                    string filelocation = String.IsNullOrEmpty(baseUNClocation) ? pDFDocToMerge.PageFilePath : Path.Combine(baseUNClocation, pDFDocToMerge.SiFolderID, pDFDocToMerge.PageFilePath);
                    //Adding new page
                    SyncfusionPDF.PdfPage page = page = document.Pages.Add();

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

                 stream = new MemoryStream();

                document.Save(stream);

                //Set the position as '0'.
                stream.Position = 0;
            }
            catch (Exception ex)
            {
                stream.Close();
                stream = null;
                Console.WriteLine(ex.ToString());
            }

            return stream;
            
        }

        public HugeMemoryStream MergePDFs_v1(List<DocumentToMigrate> pdfpages, string baseUNClocation = null)
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
                pdfdocument.EnableMemoryOptimization = true;
                mergeddocstream = new HugeMemoryStream();
                pdfdocument.Save(mergeddocstream);
                mergeddocstream.Position = 0;
            }
            return mergeddocstream;
        }

        public HugeMemoryStream MergeImages(List<DocumentToMigrate> imagefiles, string baseUNClocation = null)
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
            HugeMemoryStream stream = new HugeMemoryStream();

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


    public class HugeMemoryStream : Stream
    {
        #region Fields

        private const int PAGE_SIZE = 1024000;
        private const int ALLOC_STEP = 1024;

        private byte[][] _streamBuffers;

        private int _pageCount = 0;
        private long _allocatedBytes = 0;

        private long _position = 0;
        private long _length = 0;

        #endregion Fields

        #region Internals

        private int GetPageCount(long length)
        {
            int pageCount = (int)(length / PAGE_SIZE) + 1;

            if ((length % PAGE_SIZE) == 0)
                pageCount--;

            return pageCount;
        }

        private void ExtendPages()
        {
            if (_streamBuffers == null)
            {
                _streamBuffers = new byte[ALLOC_STEP][];
            }
            else
            {
                byte[][] streamBuffers = new byte[_streamBuffers.Length + ALLOC_STEP][];

                Array.Copy(_streamBuffers, streamBuffers, _streamBuffers.Length);

                _streamBuffers = streamBuffers;
            }

            _pageCount = _streamBuffers.Length;
        }

        private void AllocSpaceIfNeeded(long value)
        {
            if (value < 0)
                throw new InvalidOperationException("AllocSpaceIfNeeded < 0");

            if (value == 0)
                return;

            int currentPageCount = GetPageCount(_allocatedBytes);
            int neededPageCount = GetPageCount(value);

            while (currentPageCount < neededPageCount)
            {
                if (currentPageCount == _pageCount)
                    ExtendPages();

                _streamBuffers[currentPageCount++] = new byte[PAGE_SIZE];
            }

            _allocatedBytes = (long)currentPageCount * PAGE_SIZE;

            value = Math.Max(value, _length);

            if (_position > (_length = value))
                _position = _length;
        }

        #endregion Internals

        #region Stream

        public override bool CanRead => true;

        public override bool CanSeek => true;

        public override bool CanWrite => true;

        public override long Length => _length;

        public override long Position
        {
            get { return _position; }
            set
            {
                if (value > _length)
                    throw new InvalidOperationException("Position > Length");
                else if (value < 0)
                    throw new InvalidOperationException("Position < 0");
                else
                    _position = value;
            }
        }

        public override void Flush() { }

        public override int Read(byte[] buffer, int offset, int count)
        {
            int currentPage = (int)(_position / PAGE_SIZE);
            int currentOffset = (int)(_position % PAGE_SIZE);
            int currentLength = PAGE_SIZE - currentOffset;

            long startPosition = _position;

            if (startPosition + count > _length)
                count = (int)(_length - startPosition);

            while (count != 0 && _position < _length)
            {
                if (currentLength > count)
                    currentLength = count;

                Array.Copy(_streamBuffers[currentPage++], currentOffset, buffer, offset, currentLength);

                offset += currentLength;
                _position += currentLength;
                count -= currentLength;

                currentOffset = 0;
                currentLength = PAGE_SIZE;
            }

            return (int)(_position - startPosition);
        }

        public override long Seek(long offset, SeekOrigin origin)
        {
            switch (origin)
            {
                case SeekOrigin.Begin:
                    break;

                case SeekOrigin.Current:
                    offset += _position;
                    break;

                case SeekOrigin.End:
                    offset = _length - offset;
                    break;

                default:
                    throw new ArgumentOutOfRangeException("origin");
            }

            return Position = offset;
        }

        public override void SetLength(long value)
        {
            if (value < 0)
                throw new InvalidOperationException("SetLength < 0");

            if (value == 0)
            {
                _streamBuffers = null;
                _allocatedBytes = _position = _length = 0;
                _pageCount = 0;
                return;
            }

            int currentPageCount = GetPageCount(_allocatedBytes);
            int neededPageCount = GetPageCount(value);

            // Removes unused buffers if decreasing stream length
            while (currentPageCount > neededPageCount)
                _streamBuffers[--currentPageCount] = null;

            AllocSpaceIfNeeded(value);

            if (_position > (_length = value))
                _position = _length;
        }

        public override void Write(byte[] buffer, int offset, int count)
        {
            int currentPage = (int)(_position / PAGE_SIZE);
            int currentOffset = (int)(_position % PAGE_SIZE);
            int currentLength = PAGE_SIZE - currentOffset;

            long startPosition = _position;

            AllocSpaceIfNeeded(_position + count);

            while (count != 0)
            {
                if (currentLength > count)
                    currentLength = count;

                Array.Copy(buffer, offset, _streamBuffers[currentPage++], currentOffset, currentLength);

                offset += currentLength;
                _position += currentLength;
                count -= currentLength;

                currentOffset = 0;
                currentLength = PAGE_SIZE;
            }
        }

        #endregion Stream
    }


}
