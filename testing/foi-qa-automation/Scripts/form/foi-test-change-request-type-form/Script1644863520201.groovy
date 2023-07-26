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
import groovy.json.JsonSlurper as JsonSlurper

WebUI.maximizeWindow()

//WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)
'\r\n'
WebUI.click(findTestObject('Page_foi.flow/queue/button_Add Request'), FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/request type options/li_general'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Email_MuiInputBase'), 
    0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/div_CHILD DETAILS section'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/div_ON BEHALF OF DETAILS section'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'), 0)

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'), 
        'color'), 'rgba(255, 0, 0, 1)', false)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/request type options/li_personal'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'), 0)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/div_CHILD DETAILS section'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/div_CHILD DETAILS section'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/div_ON BEHALF OF DETAILS section'), 0)

WebUI.closeBrowser()

@com.kms.katalon.core.annotation.SetUp
def setup() {
    WebUI.openBrowser(GlobalVariable.BASE_URL)

    WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)
}

