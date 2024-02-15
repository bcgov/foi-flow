namespace FOIMOD.CFD.DocMigration.Utils.UnitTests
{
    [TestClass]
    public class AXISFolderToMODSectionTest
    {

        [TestInitialize]
        public void AXISFolderToMODSectionTestInit()
        {
        }

        [TestMethod]
        public void GetMatchingSectionByFolderName_ExactMatchTest()
        {
            using (AXISFolderToMODSectionUtil aXISFolderToMODSectionUtil =
                new AXISFolderToMODSectionUtil(
                    "C:\\Abindev\\foi-flow\\datamigrations" +
                    "\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.ConsoleApp.DocMigration" +
                    "\\sectionmapping\\axistomodsectionmapping.json"))
            {

                var resultexactmatch_case0 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("INTAKE, ASSESSMENT & RESPONSE");
                Assert.AreEqual("INTAKE ASSESSMENT AND RESPONSE", resultexactmatch_case0);


                var resultexactmatch_case1 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("AGREEMENTS");
                Assert.AreEqual("AGREEMENTS", resultexactmatch_case1);


                var resultexactmatch_case2 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("ASSESSMENTS & SERVICE PLANS (INT)");
                Assert.AreEqual("INTERNAL ASSESSMENTS AND SERVICE PLANS", resultexactmatch_case2);

                var resultexactmatch_case3 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("FS CPF 1-9C8LS_6.1_RappProg_ProgRep");
                Assert.AreEqual("TBD", resultexactmatch_case3);

            }
        }

        [TestMethod]
        public void GetMatchingSectionByFolderName_LastOccurenceTest()
        {
            using (AXISFolderToMODSectionUtil aXISFolderToMODSectionUtil =
                new AXISFolderToMODSectionUtil(
                    "C:\\Abindev\\foi-flow\\datamigrations" +
                    "\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.ConsoleApp.DocMigration" +
                    "\\sectionmapping\\axistomodsectionmapping.json"))
            {


                var possiblesectioninlast_case0= aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("FS6666666_2.5_Notes");
                Assert.AreEqual("Notes", possiblesectioninlast_case0);

                var possiblesectioninlast_case1 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("AH00009103_1.1_PersonalHistory");
                Assert.AreEqual("PERSONAL HISTORY AND RECORDING", possiblesectioninlast_case1);

                var possiblesectioninlast_case2 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("CS00122224_13.10_EducationTrainingPlanning");
                Assert.AreEqual("EDUCATION, EMPLOYMENT AND TRAINING", possiblesectioninlast_case2);

                var possiblesectioninlast_case3 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("CS CPF 1-2CO-4355_2.8_FamilyGroupConferencingFamilyMediation");
                Assert.AreEqual("FAMILY GROUP", possiblesectioninlast_case3);

                var possiblesectioninlast_case4 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("FS00157029_1.3_Incident");
                Assert.AreEqual("INCIDENTS", possiblesectioninlast_case4);

                var possiblesectioninlast_case5 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("CS CPF 1-2NE-3133_1.2_Document");
                Assert.AreEqual("DOCS", possiblesectioninlast_case5);

                var possiblesectioninlast_case6 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("1-1 Recording");
                Assert.AreEqual("RECORDINGS", possiblesectioninlast_case6);

                var possiblesectioninlast_case7 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("1-5 External Reports");
                Assert.AreEqual("EXTERNAL ASSESSMENTS AND REPORTS", possiblesectioninlast_case7);

           
            }
        }


        [TestMethod]
        public void GetMathingSectionByRandonTest()
        {


            using (AXISFolderToMODSectionUtil aXISFolderToMODSectionUtil =
                new AXISFolderToMODSectionUtil(
                    "C:\\Abindev\\foi-flow\\datamigrations" +
                    "\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.ConsoleApp.DocMigration" +
                    "\\sectionmapping\\axistomodsectionmapping.json"))
            {

                var possiblesectioninlast_case7 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("ABC_CDEF_sdfsdf_sdfds");
                Assert.AreEqual("TBD", possiblesectioninlast_case7);

            }
        }


        [TestMethod]
        public void GetMathingSectionByICMFolderNamesTest()
        {

            using (AXISFolderToMODSectionUtil aXISFolderToMODSectionUtil =
                new AXISFolderToMODSectionUtil(
                    "C:\\Abindev\\foi-flow\\datamigrations" +
                    "\\FOIMOD.CFD.ConsoleApp.DocMigration\\FOIMOD.CFD.ConsoleApp.DocMigration" +
                    "\\sectionmapping\\axistomodsectionmapping.json"))
            {


                var possiblesectioninlast_case1 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("DOUGAN, Taylor Incident 1-23184649960");
                Assert.AreEqual("ICM-Incident", possiblesectioninlast_case1);

                var possiblesectioninlast_case2 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("LA ROCHELLE, Ronald  ICM Memo 1-31691931888");
                Assert.AreEqual("ICM-Memo", possiblesectioninlast_case2);

                var possiblesectioninlast_case3 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("TARBOY, Janet ICM RE Complaint Incident Report 1-12580147369");
                Assert.AreEqual("ICM-Complaint Report", possiblesectioninlast_case3);

                var possiblesectioninlast_case4 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("LAUGHY, Laura-Ann Mae ICM FS Case Report 1-3402-141523");
                Assert.AreEqual("ICM-FS Case Report", possiblesectioninlast_case4);

                var possiblesectioninlast_case5 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("BAYNES, Kiyl Keith ICM SP Case Report 1-17124811018");
                Assert.AreEqual("ICM-SP Case Report", possiblesectioninlast_case5);

                var possiblesectioninlast_case6 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("BOLTON, Taylor AH Case 1-51214824525");
                Assert.AreEqual("ICM-AH Case Report", possiblesectioninlast_case6);

                var possiblesectioninlast_case7 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("TARBOY, Janet ICM RE Case Report 1-11213-3997");
                Assert.AreEqual("ICM-RE Case Report", possiblesectioninlast_case7);

                var possiblesectioninlast_case8 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("LAUGHY, Arial  ICM CS Case Report 1-3017-48209");
                Assert.AreEqual("ICM-CS Case Report", possiblesectioninlast_case8);

                var possiblesectioninlast_case9 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("HEATH, Janet   CIC roll 287");
                Assert.AreEqual("TBD", possiblesectioninlast_case9);

                var possiblesectioninlast_case10 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("HEATH, Janet   CIC roll 287");
                Assert.AreEqual("TBD", possiblesectioninlast_case10);

                var possiblesectioninlast_case11 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("FS00157029_1.11_CDMediaFile");
                Assert.AreEqual("TBD", possiblesectioninlast_case11);

                var possiblesectioninlast_case12 = aXISFolderToMODSectionUtil.GetFOIMODSectionByAXISFolder("LA ROCHELLE, Ronald ICM Service Request 1-28455143062");
                Assert.AreEqual("ICM-Service Request", possiblesectioninlast_case12);

            }


        }


    }
}
