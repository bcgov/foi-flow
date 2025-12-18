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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : findTestData('Login Credentials').getValue(
            'Password', 6), ('username') : findTestData('Login Credentials').getValue('Username', 6), ('firstname') : findTestData(
            'Login Credentials').getValue('First Name', 6), ('lastname') : findTestData('Login Credentials').getValue('Last Name', 
            6), ('applicantFirstname') : '', ('applicantLastname') : '', ('category') : '', ('email') : findTestData('Sample Applicant').getValue(
            'email', 1), ('streetAddress') : findTestData('Sample Applicant').getValue('streetAddress', 1), ('streetAddress2') : findTestData(
            'Sample Applicant').getValue('streetAddress2', 1), ('city') : findTestData('Sample Applicant').getValue('city', 
            1), ('province') : findTestData('Sample Applicant').getValue('province', 1), ('country') : findTestData('Sample Applicant').getValue(
            'country', 1), ('postalCode') : findTestData('Sample Applicant').getValue('postalCode', 1), ('homePhone') : findTestData(
            'Sample Applicant').getValue('homePhone', 1), ('description') : findTestData('Sample Applicant').getValue('description', 
            1), ('startDate') : '', ('receivedDate') : '', ('receivedMode') : '', ('requestType') : '', ('deliveryMode') : ''], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/assignee dropdown/input_ministry assigned to iao view'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/input_ministry assigned to iao view'), 
    'value', 'EDU Ministry Team', 0)

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/input_ministry assigned to iao view'), 
    'disabled', 0, FailureHandling.STOP_ON_FAILURE)

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            8), ('username') : findTestData('Login Credentials').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/input_Assigned'), 'disabled', 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/div_ministry assigned to'), 'Unassigned')

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/div_ministry assigned to'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee EDU ministry team'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee foiedu, foiedu'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee Unassigned'), 
    0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee Unassigned'), 
    'aria-disabled', 'true', 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee EDU ministry team'), 
    'aria-disabled', 'true', 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee foiedu, foiedu'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/div_ministry assigned to'), (findTestData('Login Credentials').getValue(
        'Last Name', 8) + ', ') + findTestData('Login Credentials').getValue('First Name', 8))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division dropdown'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/li_Deputy Ministers Office'))

WebUI.click(findTestObject('Records/input_Select Division Stage_mui-53'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Assigned to Division'))

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/div_ministry assigned to'), (findTestData('Login Credentials').getValue(
        'Last Name', 8) + ', ') + findTestData('Login Credentials').getValue('First Name', 8))

WebUI.navigateToUrl(GlobalVariable.BASE_URL, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 ministry assignee'), 'Foiedu, Foiedu')

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            6), ('username') : findTestData('Login Credentials').getValue('Username', 6)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/input_ministry assigned to iao view'), 
    'value', 'foiedu, foiedu', 0)

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/input_ministry assigned to iao view'), 
    'disabled', 0, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.closeBrowser()

