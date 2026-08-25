using FOIMOD.CFD.DocMigration.Models;
using FOIMOD.CFD.DocMigration.Models.Document;
using FOIMOD.CFD.DocMigration.Utils;

namespace FOIMOD.CFD.DocMigration.Utils.UnitTests;

[TestClass]
public class TargetedRecordMigrationRulesTest
{
    [TestMethod]
    public void ResolveUploadTargetPreservesConfiguredObjectName()
    {
        var item = new TargetedRecordMigrationItem
        {
            FileNumber = "CFD-2022-23413",
            Key = "CFD-2022-23413/016d1094-eda4-456d-b139-e3c2ae1d4f31.pdf"
        };

        var target = TargetedRecordMigrationRules.ResolveUploadTarget(
            "syncfusion_fix",
            item);

        Assert.AreEqual("syncfusion_fix/CFD-2022-23413", target.SubFolderPath);
        Assert.AreEqual(
            "016d1094-eda4-456d-b139-e3c2ae1d4f31.pdf",
            target.DestinationFileName);
    }

    [TestMethod]
    public void ResolveUploadTargetRejectsAKeyForAnotherRequest()
    {
        var item = new TargetedRecordMigrationItem
        {
            FileNumber = "CFD-2022-23413",
            Key = "CFD-2022-99999/016d1094-eda4-456d-b139-e3c2ae1d4f31.pdf"
        };

        Assert.ThrowsException<InvalidOperationException>(() =>
            TargetedRecordMigrationRules.ResolveUploadTarget("syncfusion_fix", item));
    }

    [TestMethod]
    public void RequireSingleDocumentRejectsAnAmbiguousLogicalFilename()
    {
        var records = new List<DocumentToMigrate>
        {
            new() { IDocID = 10 },
            new() { IDocID = 20 }
        };

        Assert.ThrowsException<InvalidOperationException>(() =>
            TargetedRecordMigrationRules.RequireSingleDocumentID(
                records,
                "CFD-2022-23413",
                "duplicate-name.pdf"));
    }

    [TestMethod]
    public void ValidateSourceFilesRejectsAPathOutsideTheRecordsRoot()
    {
        var recordsRoot = Path.Combine(Path.GetTempPath(), "axis-records");
        var pages = new List<DocumentToMigrate>
        {
            new()
            {
                SiFolderID = "..",
                PageFilePath = "outside.pdf"
            }
        };

        Assert.ThrowsException<InvalidOperationException>(() =>
            TargetedRecordMigrationRules.ValidateSourceFiles(recordsRoot, pages));
    }

}
