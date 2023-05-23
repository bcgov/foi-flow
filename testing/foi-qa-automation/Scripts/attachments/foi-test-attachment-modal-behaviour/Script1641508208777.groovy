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
import groovy.json.JsonSlurper as JsonSlurper

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'), 'Unopened')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments')

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/attachment/button_Add Attachment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/button_Add Attachment'), '+ Add Attachment')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Add Attachment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/attachment/button_Add Files'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 'Add Attachment')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Add Attachment'), FailureHandling.STOP_ON_FAILURE)

//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/p_File over 500 mb error'), 0)

//WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
  //  '/Test Attachments/500mb.pdf')

//WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/li_uploaded attachment 1'), 0)

//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/p_File over 500 mb error'), 0)

//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/p_File invalid type'), 0)

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/invalidfiletype.bin')

WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/li_uploaded attachment 1'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/p_File invalid type'), 0)

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/download.png')

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/attachment_uploaded'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/li_uploaded attachment 1'), 'download.png')

WebUI.click(findTestObject('Page_foi.flow/attachment/i_remove uploaded attachment 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/li_uploaded attachment 1'), 0)

WebUI.uploadFileWithDragAndDrop(findTestObject('Page_foi.flow/attachment/div_Add Files'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/test.docx', FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/attachment_uploaded'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/li_uploaded attachment 1'), 'test.docx')

WebUI.click(findTestObject('Page_foi.flow/attachment/i_remove uploaded attachment 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), ((RunConfiguration.getProjectDir() + 
    '/Test Attachments/test.docx\n') + RunConfiguration.getProjectDir()) + '/Test Attachments/test2.docx')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/attachment_uploaded'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/li_uploaded attachment 1'), 'test.docx')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/attachment_uploaded2'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/attachment_uploaded2'), 'test2.docx')

WebUI.click(findTestObject('Page_foi.flow/attachment/i_remove uploaded attachment 2'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/i_remove uploaded attachment 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.uploadFileWithDragAndDrop(findTestObject('Page_foi.flow/attachment/div_Add Files'), ((RunConfiguration.getProjectDir() + 
    '/Test Attachments/test.docx\n') + RunConfiguration.getProjectDir()) + '/Test Attachments/test2.docx')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/attachment_uploaded'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/li_uploaded attachment 1'), 'test.docx')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/attachment_uploaded2'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/attachment_uploaded2'), 'test2.docx')

WebUI.click(findTestObject('Page_foi.flow/attachment/i_remove uploaded attachment 2'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/i_remove uploaded attachment 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/test.docx')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/p_upload file same name'), 0)

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/test.docx')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/p_upload file same name'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyAlertPresent(0, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyMatch(WebUI.getAlertText(), 'Are you sure you want to leave? Your changes will be lost.', false)

WebUI.dismissAlert()

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyAlertPresent(0, FailureHandling.STOP_ON_FAILURE)

WebUI.acceptAlert()

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.closeBrowser()

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

