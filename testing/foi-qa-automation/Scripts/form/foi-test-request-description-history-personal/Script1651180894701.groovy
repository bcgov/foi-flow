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

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : password, ('username') : username], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + 
            firstname]))

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_AXIS ID Number'), 'ABC-2099-' + requestID)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/applicant details/div_Category'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/form/inputs/applicant details/category dropdown/li_' + findTestData(
            'Sample Applicant').getValue('category', 1)))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description'), 0)

if (WebUI.getText(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'), FailureHandling.STOP_ON_FAILURE) == 
'general') {
    WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'))
}

WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/form/description history/button_Description History'))

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description'), 'test analyst update')

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request description/span_EDU_checkmark'), 0)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Delivery Mode'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/delivery mode options/li_Secure File Transfer'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/request type options/li_personal'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Intake in Progress', 
    0)

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/form/description history/button_Description History'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/address/input_Country'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/description history/button_Description History'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/description history/p_request description history entry 1'), 
    description)

assert WebUI.getText(findTestObject('Page_foi.flow/form/description history/p_request description history entry 1 user and time'), 
    FailureHandling.STOP_ON_FAILURE).contains('Online Form')

WebUI.click(findTestObject('Page_foi.flow/form/description history/p_request description history entry 2 user and time'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/description history/p_request description history entry 2'), 
    description + 'test analyst update')

assert WebUI.getText(findTestObject('Page_foi.flow/form/description history/p_request description history entry 2 user and time'), 
    FailureHandling.STOP_ON_FAILURE).contains(GlobalVariable.username)

WebUI.click(findTestObject('Page_foi.flow/form/description history/button_Close'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            8), ('username') : findTestData('Login Credentials').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/div_Ministry Applicant Details First Name'), 
    0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/div_Ministry Applicant Details First Name'), applicantFirstname)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/div_Ministry Applicant Details Last Name'), 
    0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/div_Ministry Applicant Details Last Name'), applicantLastname)

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/form/description history/button_Description History'))

WebUI.click(findTestObject('Page_foi.flow/form/description history/button_Description History'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/description history/p_request description history entry 1'), 
    description)

assert WebUI.getText(findTestObject('Page_foi.flow/form/description history/p_request description history entry 1 user and time'), 
    FailureHandling.STOP_ON_FAILURE).contains('Online Form')

WebUI.click(findTestObject('Page_foi.flow/form/description history/p_request description history entry 2 user and time'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/description history/p_request description history entry 2'), 
    description + 'test analyst update')

assert WebUI.getText(findTestObject('Page_foi.flow/form/description history/p_request description history entry 2 user and time'), 
    FailureHandling.STOP_ON_FAILURE).contains(GlobalVariable.username)

WebUI.click(findTestObject('Page_foi.flow/form/description history/button_Close'))

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            1), ('username') : findTestData('Login Credentials').getValue('Username', 1)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.closeBrowser()

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

