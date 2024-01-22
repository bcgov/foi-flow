using MCS.FOI.OCRtoPDF;
using System.IO;

namespace FOIMOD.CFD.DocMigration.OCR.Tests
{
    [TestClass]
    public class OCRToPdfTest
    {
        [TestMethod]
        public void OCRTest()
        {
            Syncfusion.Licensing.SyncfusionLicenseProvider.RegisterLicense("<License here");

            FileStream fileStream = new FileStream(Path.Combine(getSourceFolder(), "scansmpl.pdf"), FileMode.Open, FileAccess.Read);
            OCRTOPdf.TessaractPath = "C:\\AOT\\FOI\\Source\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR\\Tesseractbinaries_core\\Windows\\x64";
            OCRTOPdf.TessaractLanguagePath = "C:\\AOT\\FOI\\Source\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR\\tessdata";
            using MemoryStream ocrdstream = OCRTOPdf.ConvertToSearchablePDF(fileStream);
            using FileStream file = new FileStream(Path.Combine(getSourceFolder(),"ocrdpdf.pdf"), FileMode.Create, FileAccess.Write);
            ocrdstream.WriteTo(file);
            file.Close();
            ocrdstream.Close();

        }

        private string getSourceFolder()
        {
            return "C:\\AOT\\FOI\\Source\\foi-flow\\datamigrations\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.DocMigration.OCR.Tests";
        }
    }
}