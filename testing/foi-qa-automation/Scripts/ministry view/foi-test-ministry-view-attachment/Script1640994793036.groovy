import static com.kms.katalon.core.testcase.TestCaseFactory.findTestCase
import static com.kms.katalon.core.testdata.TestDataFactory.findTestData
import static com.kms.katalon.core.testobject.ObjectRepository.findTestObject

import org.testng.Assert

import com.kms.katalon.core.configuration.RunConfiguration
import com.kms.katalon.core.model.FailureHandling
import com.kms.katalon.core.util.KeywordUtil
import com.kms.katalon.core.webui.keyword.WebUiBuiltInKeywords as WebUI

import internal.GlobalVariable as GlobalVariable

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : GlobalVariable.password, ('username') : GlobalVariable.username
        , ('firstname') : GlobalVariable.firstname, ('lastname') : GlobalVariable.lastname, ('applicantFirstname') : '', ('applicantLastname') : ''
        , ('category') : '', ('email') : findTestData('Sample Applicant').getValue('email', 1), ('streetAddress') : findTestData('Sample Applicant').getValue('streetAddress', 1)
        , ('streetAddress2') : findTestData('Sample Applicant').getValue('streetAddress2', 1), ('city') : findTestData('Sample Applicant').getValue('city', 1)
        , ('province') : findTestData('Sample Applicant').getValue('province', 1), ('country') : findTestData('Sample Applicant').getValue('country', 1)
        , ('postalCode') : findTestData('Sample Applicant').getValue('postalCode', 1), ('homePhone') : findTestData('Sample Applicant').getValue('homePhone', 1)
        , ('description') : findTestData('Sample Applicant').getValue('description', 1), ('startDate') : '', ('receivedDate') : ''
        , ('receivedMode') : '', ('requestType') : '', ('deliveryMode') : ''], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_Open'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/li_Call For Records'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.delay(1, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Add Attachment'), FailureHandling.STOP_ON_FAILURE)

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + '/Test Attachments/test.docx')

WebUI.click(findTestObject('Page_foi.flow/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/button_Sign Out'), FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('New Test Data').getValue('Password', 8)
        , ('username') : findTestData('New Test Data').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header ID NUMBER'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header APPLICANT TYPE'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header REQUEST TYPE'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header CURRENT STATE'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/queue/div_queue header CURRENT STATE'), 'aria-sort', 'ascending', 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header ASSIGNED TO'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header RECORDS DUE'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header LDD'), 0)

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 'background-color'), 'rgba(207, 215, 227, 1)', 
    false)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/div_attachements list row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_attachments row 1 actions'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/attachment/button_Attachments Download'), FailureHandling.STOP_ON_FAILURE)

//'Define Custom Path where file needs to be downloaded'
//def downloadPath = RunConfiguration.getProjectDir() + '/Test Download Folder/'
//
//File file = new File(downloadPath, 'test.docx')
//
//Assert.assertFalse(file.exists())
//
//'Clicking on a Link text to download a file'
//WebUI.click(findTestObject('Page_foi.flow/attachment/button_Attachments Download'), FailureHandling.STOP_ON_FAILURE)
//'Wait for Some time so that file gets downloaded and Stored in user defined path'
//WebUI.delay(10)
// 
//'Verifying the file is download in the User defined Path'
//Assert.assertTrue(isFileDownloaded(downloadPath, 'test.docx'), 'Failed to download Expected document')
// 
//boolean isFileDownloaded(String downloadPath, String fileName) {
//	long timeout = 5 * 60 * 1000
//	long start = new Date().getTime()
//	boolean downloaded = false
//	File file = new File(downloadPath, fileName)
//	while (!downloaded) {
//		KeywordUtil.logInfo("Checking file exists ${file.absolutePath}")
//		downloaded = file.exists()
//		if (downloaded) {
//			file.delete() // remove this line if you want to keep the file
//		} else {
//			long now = new Date().getTime()
//			if (now - start > timeout) {
//				break
//			}
//			Thread.sleep(3000)
//		}
//	}
//	return downloaded
//}

