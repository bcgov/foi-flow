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

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID, ('clickOnRequest') : false], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row by id state', [('requestID') : 'U-00' + 
            requestID]), 'Unopened')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row by id assignee', [('requestID') : 'U-00' + 
            requestID]), 'Unassigned')

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/queue/div_request queue row by id', [('requestID') : 'U-00' + 
                requestID]), 'background-color'), 'rgba(207, 215, 227, 1)', false)

WebUI.scrollToElement(findTestObject('Page_foi.flow/queue/div_request queue row by id', [('requestID') : 'U-00' + requestID]), 
    0)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row by id', [('requestID') : 'U-00' + requestID]))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'), 'Unopened')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Unopened'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Intake In Progress'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Intake In Progress'), 'aria-disabled', 
    'true', 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Unopened'), FailureHandling.STOP_ON_FAILURE)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    WS.verifyResponseStatusCode(response, 200)

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WebUI.openBrowser(GlobalVariable.BASE_URL)

    WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)
}
