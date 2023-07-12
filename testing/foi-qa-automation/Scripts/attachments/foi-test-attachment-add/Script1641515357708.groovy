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

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID, ('clickOnRequest') : true], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'), 'Unopened')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments')

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Add Attachment'), FailureHandling.STOP_ON_FAILURE)

println(RunConfiguration.getProjectDir() + '/Test Attachments')

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/test.docx')

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/div_attachments list row 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/div_attachment list 1 name'), 'test.docx')

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/div_attachment list 1 creator'), (lastname + ', ') + firstname)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/div_attachment list 1 created time'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments (1)')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/div_attachments list row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Add Attachment'), FailureHandling.STOP_ON_FAILURE)

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/test2.docx')

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/test2.pdf')

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments (3)')

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/div_attachment list 1 name'), 'test2.pdf')

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/div_attachment list 2 name'), 'test2.docx')

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/div_attachment list 3 name'), 'test2.pdf')

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/div_attachment list 1 name'), 'test2.pdf')

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/div_attachment list 2 name'), 'test2.docx')

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/div_attachment list 3 name'), 'test2.pdf')

WebUI.click(findTestObject('Page_foi.flow/attachment/button_attachments row 1 actions'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Attachments Delete'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments (2)')

WebUI.click(findTestObject('Page_foi.flow/attachment/button_attachments row 1 actions'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Attachments Delete'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments (1)')

WebUI.click(findTestObject('Page_foi.flow/attachment/button_attachments row 1 actions'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Attachments Delete'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'), 'Attachments')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/div_attachments list row 1'), 0)

WebUI.closeBrowser()

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

