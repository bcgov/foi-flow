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
import com.kms.katalon.core.webui.common.WebUiCommonHelper as WebUiCommonHelper
import com.kms.katalon.core.webui.keyword.WebUiBuiltInKeywords as WebUI
import com.kms.katalon.core.windows.keyword.WindowsBuiltinKeywords as Windows
import internal.GlobalVariable as GlobalVariable
import org.openqa.selenium.Keys as Keys
import groovy.json.JsonSlurper as JsonSlurper
import org.openqa.selenium.WebElement as WebElement

def today = new Date()

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

//WebUI.delay(10)
assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned parent'), 'class').contains(
    'Mui-error') == true

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'), 
        'color'), 'rgba(255, 0, 0, 1)', false)

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Delivery Mode parent'), 'class').contains(
    'Mui-error') == true

WebUI.click(findTestObject('Page_foi.flow/form/inputs/applicant details/div_Category'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Business'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Individual'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Interest Group'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Law Firm'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Media'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Political Party'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Researcher'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Other Governments'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Other Public Body'), 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Individual'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/request details/input_Start Date'), 'min', WebUI.getAttribute(
        findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date'), 'value'), 0)

//WebUI.executeJavaScript("alert('This is an alert')", null)
def laterDate = new Date().plus(10)

WebElement element = WebUiCommonHelper.findWebElement(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date'), 
    30)

//
WebUI.executeJavaScript(('Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set.call(arguments[0], "' + 
    laterDate.format('yyyy-MM-dd')) + '")', Arrays.asList(element))

WebUI.executeJavaScript('console.log(arguments[0])', Arrays.asList(element))

WebUI.executeJavaScript('arguments[0].dispatchEvent(new Event(\'change\', { bubbles: true}))', Arrays.asList(element))

//WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date'), laterDate.format('yyyyyyMMdd'))
//WebUI.sendKeys(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date'), Keys.chord('0','0','2','2','2','0','0','3','0','5'))
//WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date'), FailureHandling.STOP_ON_FAILURE)
//System.exit(0)
WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/request details/input_Start Date'), 'min', WebUI.getAttribute(
        findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date'), 'value'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/request details/input_Start Date'), 'value', 
    laterDate.format('yyyy-MM-dd'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/request description/input_Search Start Date'), 
    'max', today.format('yyyy-MM-dd'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/request description/input_Search End Date'), 
    'max', today.format('yyyy-MM-dd'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/request description/input_Search End Date'), 
    'min', WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request description/input_Search Start Date'), 'value'), 
    0)

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/request description/input_EDU checkbox'), 'checked', 
    0)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_EDU_checkmark'))

WebUI.verifyElementNotHasAttribute(findTestObject('Page_foi.flow/form/inputs/request description/input_EDU checkbox'), 'checked', 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_EDU_checkmark'))

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/request description/input_EDU checkbox'), 'checked', 
    0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Mode'), 'aria-disabled', 
    'true', 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Mode'), 'Online Form')

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'), 'class', 'tablinks active', 
    0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'class', 'tablinks', 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'), 'class', 'tablinks', 
    0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'class', 'tablinks active', 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/label_All Comments'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/label_Request History'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/label_User Comments'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/a_FOI'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/i_Home logo'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/a_FOI'), 'href', GlobalVariable.BASE_URL + 
    '/foi/dashboard', 0)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

