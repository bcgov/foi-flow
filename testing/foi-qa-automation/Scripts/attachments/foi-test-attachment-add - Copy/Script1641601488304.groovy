import static com.kms.katalon.core.checkpoint.CheckpointFactory.findCheckpoint
import static com.kms.katalon.core.testcase.TestCaseFactory.findTestCase
import static com.kms.katalon.core.testdata.TestDataFactory.findTestData
import static com.kms.katalon.core.testobject.ObjectRepository.findTestObject
import static com.kms.katalon.core.testobject.ObjectRepository.findWindowsObject
import com.kms.katalon.core.checkpoint.Checkpoint as Checkpoint
import com.kms.katalon.core.cucumber.keyword.CucumberBuiltinKeywords as CucumberKW
import com.kms.katalon.core.mobile.keyword.MobileBuiltInKeywords as Mobile
import com.kms.katalon.core.model.FailureHandling as FailureHandling
import com.kms.katalon.core.testcase.TestCase as TestCase
import com.kms.katalon.core.testdata.TestData as TestData
import com.kms.katalon.core.testng.keyword.TestNGBuiltinKeywords as TestNGKW
import com.kms.katalon.core.testobject.TestObject as TestObject
import com.kms.katalon.core.webservice.keyword.WSBuiltInKeywords as WS
import com.kms.katalon.core.webui.keyword.WebUiBuiltInKeywords as WebUI
import com.kms.katalon.core.windows.keyword.WindowsBuiltinKeywords as Windows
import internal.GlobalVariable as GlobalVariable
import org.openqa.selenium.Keys as Keys
import com.kms.katalon.core.configuration.RunConfiguration as RunConfiguration
import com.kms.katalon.core.util.KeywordUtil as KeywordUtil
import org.testng.Assert as Assert

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1 applicant name'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'), 'Unopened')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/div_attachments list row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Add Attachment'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Add Files'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Add Files'), FailureHandling.STOP_ON_FAILURE)

//WebUI.uploadFileWithDragAndDrop(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + '/Test Attachments/test.docx')
WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/li_uploaded attachment 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_attachments row 1 actions'), FailureHandling.STOP_ON_FAILURE) //WebUI.uploadFileWithDragAndDrop(findTestObject('Page_foi.flow/attachment/div_Add Files'), RunConfiguration.getProjectDir() + '/Test Attachments/500mb.pdf', 
//    FailureHandling.STOP_ON_FAILURE)
//'Define Custom Path where file needs to be downloaded'
//def downloadPath = RunConfiguration.getProjectDir() + '/Test Download Folder'
//
//Map<String, Object> chromePrefs = new HashMap<String, Object>()
//chromePrefs.put("download.default_directory", downloadPath.replace('/', '\\'))
//RunConfiguration.setWebDriverPreferencesProperty("prefs", chromePrefs)
//
//File file = new File(downloadPath, 'test.docx')
//
//if (file.exists()) {
//	file.delete()
//}
//
//'Clicking on a Link text to download a file'
//WebUI.click(findTestObject('Page_foi.flow/attachment/button_Attachments Download'), FailureHandling.STOP_ON_FAILURE)
//
//'Wait for Some time so that file gets downloaded and Stored in user defined path'
//WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT0)
//
//'Verifying the file is download in the User defined Path'
//Assert.assertTrue(isFileDownloaded(downloadPath, 'test.docx'), 'Failed to download Expected document') // remove this line if you want to keep the file
//
//boolean isFileDownloaded(String downloadPath, String fileName) {
//    long timeout = (5 * 60) * 1000
//
//    long start = new Date().getTime()
//
//    boolean downloaded = false
//
//    File file = new File(downloadPath, fileName)
//
//    while (!(downloaded)) {
//        KeywordUtil.logInfo("Checking file exists $file.absolutePath")
//
//        downloaded = file.exists()
//
//        if (downloaded) {
////            file.delete()
//        } else {
//            long now = new Date().getTime()
//
//            if ((now - start) > timeout) {
//                break
//            }
//            
//            Thread.sleep(3000)
//        }
//    }
//    
//    return downloaded
//}

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    WS.verifyResponseStatusCode(response, 200)
}

