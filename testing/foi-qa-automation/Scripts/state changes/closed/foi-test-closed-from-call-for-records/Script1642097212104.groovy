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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('applicantFirstname') : '', ('applicantLastname') : ''
        , ('category') : '', ('email') : findTestData('Sample Applicant').getValue('email', 1), ('streetAddress') : findTestData(
            'Sample Applicant').getValue('streetAddress', 1), ('streetAddress2') : findTestData('Sample Applicant').getValue(
            'streetAddress2', 1), ('city') : findTestData('Sample Applicant').getValue('city', 1), ('province') : findTestData(
            'Sample Applicant').getValue('province', 1), ('country') : findTestData('Sample Applicant').getValue('country', 
            1), ('postalCode') : findTestData('Sample Applicant').getValue('postalCode', 1), ('homePhone') : findTestData(
            'Sample Applicant').getValue('homePhone', 1), ('description') : findTestData('Sample Applicant').getValue('description', 
            1), ('startDate') : '', ('receivedDate') : '', ('receivedMode') : '', ('requestType') : '', ('deliveryMode') : ''], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

def ldd = WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Due Date'), 'value')

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Abandoned'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.waitForElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 2)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Closed', 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Intake In Progress'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Re-Open Request'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Call For Records', 
    0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/request details/input_Due Date'), 'value', ldd, 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Page_foi.flow/comment/span_Request History Comments'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), ((findTestData('Login Credentials').getValue(
        'First Name', 1) + ' ') + findTestData('Login Credentials').getValue('Last Name', 1)) + ' changed the state of the request to Call For Records')

