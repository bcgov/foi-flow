using FOIMOD.CFD.DocMigration.DAL;
using Microsoft.Data.SqlClient;

namespace FOIMOD.CFD.DocMigration.AXIS.DAL.UnitTests;

[TestClass]
public class RecordLookupQueryTest
{
    [TestMethod]
    public void CreateCommandUsesParametersForRequestAndLogicalFilename()
    {
        const string requestNumber = "CFD-2022-23413'; DROP TABLE tblRequests;--";
        const string fileName = "Parent's record.pdf";
        using var connection = new SqlConnection();

        using var command = RecordLookupQuery.CreateCommand(
            connection,
            requestNumber,
            fileName);

        Assert.IsFalse(command.CommandText.Contains(requestNumber));
        Assert.IsFalse(command.CommandText.Contains(fileName));
        Assert.AreEqual(requestNumber, command.Parameters["@RequestNumber"].Value);
        Assert.AreEqual(fileName, command.Parameters["@FileName"].Value);
    }
}
