import static com.kms.katalon.core.checkpoint.CheckpointFactory.findCheckpoint
import groovy.json.JsonSlurper as JsonSlurper
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

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Search'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'), 'Unopened')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/div_attachments list row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Add Attachment'), FailureHandling.STOP_ON_FAILURE)

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/test.docx')

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments (1)')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_attachments row 1 actions'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Attachments Delete'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/h2_Delete Attachment'), 'Delete Attachment')

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/span_Are you sure you want to delete the attachment'), 
    'Are you sure you want to delete the attachment?')

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/div_attachments list row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_attachments row 1 actions'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Attachments Delete'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/div_attachments list row 1'), 0)

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/div_attachments list row 1'), 0)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

