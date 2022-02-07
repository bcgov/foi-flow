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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : findTestData('New Test Data').getValue('Password', 
            2), ('username') : findTestData('New Test Data').getValue('Username', 2), ('firstname') : findTestData('New Test Data').getValue(
            'First Name', 2), ('lastname') : findTestData('New Test Data').getValue('Last Name', 2), ('applicantFirstname') : ''
        , ('applicantLastname') : '', ('category') : '', ('email') : findTestData('Sample Applicant').getValue('email', 
            1), ('streetAddress') : findTestData('Sample Applicant').getValue('streetAddress', 1), ('streetAddress2') : findTestData(
            'Sample Applicant').getValue('streetAddress2', 1), ('city') : findTestData('Sample Applicant').getValue('city', 
            1), ('province') : findTestData('Sample Applicant').getValue('province', 1), ('country') : findTestData('Sample Applicant').getValue(
            'country', 1), ('postalCode') : findTestData('Sample Applicant').getValue('postalCode', 1), ('homePhone') : findTestData(
            'Sample Applicant').getValue('homePhone', 1), ('description') : findTestData('Sample Applicant').getValue('description', 
            1), ('startDate') : '', ('receivedDate') : '', ('receivedMode') : '', ('requestType') : '', ('deliveryMode') : ''], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Object Repository/Page_foi.flow/span_Description contains NO Personal Infor_c58cd5'), 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/span_MMA_checkmark'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/span_JER_checkmark'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/span_TAC_checkmark'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/span_LBR_checkmark'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_Open'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/li_Call For Records'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.delay(1, FailureHandling.STOP_ON_FAILURE)

def year = new Date().format('yyyy')

WebUI.verifyMatch('EDUC-' + year, WebUI.getText(findTestObject('Page_foi.flow/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE).substring(
        0, 9), false)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_queue header ID NUMBER'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_queue header ID NUMBER'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.verifyMatch('EDUC-' + year, WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 1 request no'), FailureHandling.STOP_ON_FAILURE).substring(
        0, 9), false)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 2'), 0)

WebUI.verifyMatch('JERI-' + year, WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 2 request no'), FailureHandling.STOP_ON_FAILURE).substring(
        0, 9), false)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 3'), 0)

WebUI.verifyMatch('LBR-' + year, WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 3 request no'), FailureHandling.STOP_ON_FAILURE).substring(
        0, 8), false)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 4'), 0)

WebUI.verifyMatch('MUNI-' + year, WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 4 request no'), FailureHandling.STOP_ON_FAILURE).substring(
        0, 9), false)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 5'), 0)

WebUI.verifyMatch('TACS-' + year, WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 5 request no'), FailureHandling.STOP_ON_FAILURE).substring(
        0, 9), false)

WebUI.click(findTestObject('Page_foi.flow/queue/div_queue header CURRENT STATE'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/li_Call For Records'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/li_Call For Records'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/li_Call For Records'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/li_Call For Records'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.delay(2)

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Sign Out'))

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-edu-options'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-jer-options'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-mma-options'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-tac-options'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-lbr-options'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-comments'), [:], FailureHandling.STOP_ON_FAILURE)

