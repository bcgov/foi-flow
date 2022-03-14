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

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Search'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1 applicant name'))

'\r\n'
WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/request type options/li_general'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Email_MuiInputBase'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/div_CHILD DETAILS section'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/div_ON BEHALF OF DETAILS section'), 0)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/request type options/li_personal'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/div_CHILD DETAILS section'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/div_CHILD DETAILS section'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/label_CHILD DETAILS'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/div_ON BEHALF OF DETAILS section'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/label_ON BEHALF OF DETAILS'), 0)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)

    WebUI.openBrowser(GlobalVariable.BASE_URL)

    WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)
}

