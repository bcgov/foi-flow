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

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/request type options/li_personal'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'))

WebUI.callTestCase(findTestCase('helper/foi-test-verify-next-assignee'), [('ministryCode') : 'EDU', ('requestType') : 'personal'], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Open', 
    0)

WebUI.refresh(FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Social Education'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Flex Team'), 0)

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'), FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            14), ('username') : findTestData('Login Credentials').getValue('Username', 14)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 assignee'), 'Social Education')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header ID NUMBER'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header APPLICANT NAME'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header APPLICANT TYPE'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header ON BEHALF OF'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header TYPE'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header CURRENT STATE'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header ASSIGNED TO'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header DAYS LEFT'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header EXT'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header NO PAGES'), 0)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 assignee'), 'Social Education')

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1 applicant name'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_Intake Team'), FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

//WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)
//
//WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')
//
//WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))
WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

//
//WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)
//
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)
WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'), FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            6), ('username') : findTestData('Login Credentials').getValue('Username', 6)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 assignee'), 'Intake Team')

WebUI.closeBrowser()

