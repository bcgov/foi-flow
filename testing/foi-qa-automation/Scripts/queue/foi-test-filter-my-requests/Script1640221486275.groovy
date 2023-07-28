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

def requestID = WebUI.getUrl(FailureHandling.STOP_ON_FAILURE).split('/')[5]

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Requests'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1 applicant name'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_User, Super'))

def requestID1 = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID1)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Requests'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID1)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

assert WebUI.getAttribute(findTestObject('Page_foi.flow/queue/div_My Requests'), 'class').contains('MuiButtonBase-root MuiChip-root MuiChip-outlined MuiChip-sizeSmall MuiChip-colorDefault MuiChip-clickable MuiChip-clickableColorDefault MuiChip-outlinedDefault css-zo9we2')

assert WebUI.getAttribute(findTestObject('Page_foi.flow/queue/div_Watching Requests'), 'class').contains('MuiButtonBase-root MuiChip-root MuiChip-outlined MuiChip-sizeSmall MuiChip-colorDefault MuiChip-clickable MuiChip-clickableColorDefault MuiChip-outlinedDefault css-zo9we2')

assert WebUI.getAttribute(findTestObject('Page_foi.flow/queue/div_My Team Requests'), 'class').contains('MuiButtonBase-root MuiChip-root MuiChip-filled MuiChip-sizeSmall MuiChip-colorDefault MuiChip-clickable MuiChip-clickableColorDefault MuiChip-filledDefault css-1uoxw5f')

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            4), ('username') : findTestData('Login Credentials').getValue('Username', 4)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Requests'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

//assert WebUI.getAttribute(findTestObject('Page_foi.flow/queue/div_My Requests'), 'class').contains('MuiChip-filledPrimary')
//assert WebUI.getAttribute(findTestObject('Page_foi.flow/queue/div_Watching Requests'), 'class').contains('MuiChip-outlinedPrimary')
//assert WebUI.getAttribute(findTestObject('Page_foi.flow/queue/div_My Team Requests'), 'class').contains('MuiChip-outlinedPrimary')
WebUI.closeBrowser()

