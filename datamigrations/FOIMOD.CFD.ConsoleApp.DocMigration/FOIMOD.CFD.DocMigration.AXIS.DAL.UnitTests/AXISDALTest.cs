using FOIMOD.CFD.DocMigration.DAL;
using Microsoft.Data.SqlClient;

namespace FOIMOD.CFD.DocMigration.AXIS.DAL.UnitTests
{
    [TestClass]
    public class AXISDALTest
    {
        [TestMethod]
        public void GetCorrespondenceLogDocsTest()
        {
            SqlConnection conn = new SqlConnection(@"Data Source=.;Initial Catalog=ATIPD;Integrated Security=True;Encrypt=False");
            DocumentsDAL documentsDAL = new DocumentsDAL(conn);
            var correspondencelogs = documentsDAL.GetCorrespondenceLogDocuments();
            Assert.IsNotNull(correspondencelogs);
            

        }
    }
}