using Amazon.S3;
using FOIMOD.CFD.DocMigration.Models.Document;
using FOIMOD.CFD.DocMigration.Models.FOIFLOWDestination;
using FOIMOD.CFD.DocMigration.Utils;
using MCS.FOI.OCRtoPDF;
using System.IO;
using System.Net;

namespace FOIMOD.CFD.DocMigration.OCR.Tests
{
    [TestClass]
    public class OCRToPdfTest
    {
        [TestMethod]
        public void OCRTest()
        {
            Syncfusion.Licensing.SyncfusionLicenseProvider.RegisterLicense("License here");

            FileStream fileStream = new FileStream(Path.Combine(getSourceFolder(), "mergeresult.pdf"), FileMode.Open, FileAccess.Read);
            OCRTOPdf.TessaractPath = "C:\\Abindev\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR\\Tesseractbinaries_core\\Windows\\x64";
            OCRTOPdf.TessaractLanguagePath = "C:\\Abindev\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR\\tessdata";
            using MemoryStream ocrdstream = OCRTOPdf.ConvertToSearchablePDF(fileStream);
            using FileStream file = new FileStream(Path.Combine(getSourceFolder(),"ocrdpdf.pdf"), FileMode.Create, FileAccess.Write);
            ocrdstream.WriteTo(file);
            file.Close();
            ocrdstream.Close();

        }

        [TestMethod]
        public void PDFMergeOCRTest1_UploadTest()
        {
            List<DocumentToMigrate> pDFDocToMerges = new List<DocumentToMigrate>();
            pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(),"samples", "DOCX1.pdf"), PageSequenceNumber = 3 });
            pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(), "samples", "cat1.pdf"), PageSequenceNumber = 2 });


            using (DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher())
            {
                using MemoryStream fs = docMigrationPDFStitcher.MergePDFs(pDFDocToMerges);                
                
                using FileStream file = new FileStream(Path.Combine(getSourceFolder(), "mergeresult.pdf"), FileMode.Create, FileAccess.Write);
                fs.WriteTo(file);
                file.Close();
                

                if(File.Exists(Path.Combine(getSourceFolder(), "mergeresult.pdf")))
                {
                    OCRTOPdf.TessaractPath = "C:\\Abindev\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR\\Tesseractbinaries_core\\Windows\\x64";
                    OCRTOPdf.TessaractLanguagePath = "C:\\Abindev\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR\\tessdata";
                    FileStream mergedfileStream = new FileStream(Path.Combine(getSourceFolder(), "mergeresult.pdf"), FileMode.Open, FileAccess.Read);
                    using MemoryStream ocrdstream = OCRTOPdf.ConvertToSearchablePDF(mergedfileStream);

                    using FileStream mergedocrfile = new FileStream(Path.Combine(getSourceFolder(), "ocrdmergedpdf.pdf"), FileMode.Create, FileAccess.Write);
                    ocrdstream.WriteTo(mergedocrfile);
                    file.Close();


                    ocrdstream.Close();
                }

            }
        }


        [TestMethod]
        public void PDFMergeOCRTest2_UploadTest()
        {
            List<DocumentToMigrate> pDFDocToMerges = new List<DocumentToMigrate>();
            pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(), "samples", "DOCX1.pdf"), PageSequenceNumber = 3 });
            pDFDocToMerges.Add(new DocumentToMigrate() { PageFilePath = Path.Combine(getSourceFolder(), "samples", "cat1.pdf"), PageSequenceNumber = 2 });


            using (DocMigrationPDFStitcher docMigrationPDFStitcher = new DocMigrationPDFStitcher())
            {
                using MemoryStream mergedfileStream = docMigrationPDFStitcher.MergePDFs(pDFDocToMerges);
                OCRTOPdf.TessaractPath = "C:\\Abindev\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR\\Tesseractbinaries_core\\Windows\\x64";
                OCRTOPdf.TessaractLanguagePath = "C:\\Abindev\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR\\tessdata";

                using MemoryStream ocrdstream = OCRTOPdf.ConvertToSearchablePDF(mergedfileStream);


                using FileStream mergedocrfile = new FileStream(Path.Combine(getSourceFolder(), "ocrdmergedpdf.pdf"), FileMode.Create, FileAccess.Write);
                ocrdstream.WriteTo(mergedocrfile);
                mergedfileStream.Close();


                ocrdstream.Close();
            }
        }




        private string getSourceFolder()
        {
            return "C:\\Abindev\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR.Tests";
        }
    }
}