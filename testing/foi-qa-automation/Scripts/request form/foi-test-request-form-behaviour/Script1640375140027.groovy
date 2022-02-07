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

def today = new Date()

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1 applicant name'))

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned parent'), 'class').contains(
    'Mui-error') == true

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/span_Description contains NO Personal Infor_c58cd5'), 
        'color'), 'rgba(255, 0, 0, 1)', false)

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Delivery Mode parent'), 'class').contains('Mui-error') == 
true

WebUI.click(findTestObject('Page_foi.flow/form/inputs/div_Category'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Business'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Individual'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Interest Group'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Law Firm'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Media'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Political Party'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Researcher'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Other Governments'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Other Public Body'), 0)

WebUI.click(findTestObject('Page_foi.flow/li_Individual'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Start Date'), 'min', WebUI.getAttribute(
        findTestObject('Page_foi.flow/form/inputs/input_Received Date'), 'value'), 0)

def tomorrow

use(groovy.time.TimeCategory, { 
        tomorrow = (new Date() + 1.day)
    })

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Received Date'), tomorrow.format('yyyyyy-MM-dd'))

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Start Date'), 'min', WebUI.getAttribute(
        findTestObject('Page_foi.flow/input_Received Date'), 'value'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Start Date'), 'value', tomorrow.format(
        'yyyy-MM-dd'), 0)

if (today.format('HHmm').toInteger() > 1630) {
    today = tomorrow
}

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Search Start Date'), 'max', today.format(
        'yyyy-MM-dd'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Search End Date'), 'max', today.format(
        'yyyy-MM-dd'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Search End Date'), 'min', WebUI.getAttribute(
        findTestObject('Page_foi.flow/input_Search Start Date'), 'value'), 0)

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/input_EDU checkbox'), 'checked', 0)

WebUI.click(findTestObject('Page_foi.flow/span_EDU_checkmark'))

WebUI.verifyElementNotHasAttribute(findTestObject('Page_foi.flow/form/inputs/input_EDU checkbox'), 'checked', 0)

WebUI.click(findTestObject('Page_foi.flow/span_EDU_checkmark'))

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/input_EDU checkbox'), 'checked', 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Received Mode'), 'aria-disabled', 'true', 
    0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/inputs/input_Received Mode'), 'Online Form')

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

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/label_Request History'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/label_User Comments'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/a_FOI'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/a_FOI'), 'href', GlobalVariable.BASE_URL + 
    '/foi/dashboard', 0)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    WS.verifyResponseStatusCode(response, 200)
}

