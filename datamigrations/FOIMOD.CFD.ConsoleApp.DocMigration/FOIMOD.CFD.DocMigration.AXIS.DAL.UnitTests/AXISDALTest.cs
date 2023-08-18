using FOIMOD.CFD.DocMigration.DAL;
using Microsoft.Data.SqlClient;

namespace FOIMOD.CFD.DocMigration.AXIS.DAL.UnitTests
{
    [TestClass]
    public class AXISDALTest
    {
        SqlConnection conn = new SqlConnection(@"Data Source=.;Initial Catalog=ATIPD;Integrated Security=True;Encrypt=False");

        [TestMethod]
        public void GetCorrespondenceLogDocsTest()
        {
            
            DocumentsDAL documentsDAL = new DocumentsDAL(conn);
            var correspondencelogs = documentsDAL.GetCorrespondenceLogDocuments();
            Assert.IsNotNull(correspondencelogs);
            
        }


        [TestMethod]
        public void GetRecordsTest()
        {

            DocumentsDAL documentsDAL = new DocumentsDAL(conn);
            var correspondencelogs = documentsDAL.GetRecordsByRequest("NGD-2015-50137");
            Assert.IsNotNull(correspondencelogs);

        }
    }
}