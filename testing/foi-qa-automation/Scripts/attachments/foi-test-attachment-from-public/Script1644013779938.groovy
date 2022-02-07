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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : findTestData('New Test Data').getValue('Password', 
            6), ('username') : findTestData('New Test Data').getValue('Username', 6), ('firstname') : findTestData('New Test Data').getValue(
            'First Name', 6), ('lastname') : findTestData('New Test Data').getValue('Last Name', 6), ('sendRequest') : false], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/div_attachment list 1 name'), findTestData('Sample Applicant').getValue(
        'attachmentName', 1))

WebUI.click(findTestObject('Page_foi.flow/attachment/button_attachments row 1 actions'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/button_Attachments Delete'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/button_Attachments Rename'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/button_Attachments Download'), 0)

WebUI.click(findTestObject('Page_foi.flow/body'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_Open'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/li_Call For Records'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.waitForElementClickable(findTestObject('Page_foi.flow/button_Sign Out'), 2)

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('New Test Data').getValue('Password', 8)
        , ('username') : findTestData('New Test Data').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/div_attachment list 1 name'), findTestData('Sample Applicant').getValue(
        'attachmentName', 1))

WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/attachment/button_attachments row 1 actions'), FailureHandling.STOP_ON_FAILURE)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequestWithAttachment'))

    WS.verifyResponseStatusCode(response, 200)
}

