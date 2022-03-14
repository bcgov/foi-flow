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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : GlobalVariable.password, ('username') : GlobalVariable.username
        , ('firstname') : GlobalVariable.firstname, ('lastname') : GlobalVariable.lastname, ('sendRequest') : false, ('requestID') : request2ID], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/queue/div_queue header CURRENT STATE'), 'aria-sort', 'descending', 
    0)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), request1ID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 state'), 'Unopened')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 request no'), 'U-00' + request1ID)

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 'background-color'), 
    'rgba(207, 215, 227, 1)', false)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), 'intake in progress')

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 state'), 'Intake In Progress')

WebUI.verifyNotMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 'background-color'), 
    'rgba(207, 215, 227, 1)', false)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    request1ID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)

    response = WS.sendRequest(findTestObject('FoiRawRequest'))

    request2ID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

