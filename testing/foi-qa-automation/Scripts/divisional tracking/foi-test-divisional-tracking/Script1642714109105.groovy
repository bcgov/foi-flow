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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'), 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_MMA_checkmark'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_JER_checkmark'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_TAC_checkmark'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_LBR_checkmark'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/request type options/li_general'))

def requestID = WebUI.getUrl(FailureHandling.STOP_ON_FAILURE).split('/')[5]

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

def year = new Date().format('yyyy')

requestID = ((year + '-') + requestID)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_queue header ID NUMBER'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_queue header ID NUMBER'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

assert WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 1 request no'), FailureHandling.STOP_ON_FAILURE).contains(
    'EDUC-' + requestID)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 2'), 0)

assert WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 2 request no'), FailureHandling.STOP_ON_FAILURE).contains(
    'JERI-' + requestID)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 3'), 0)

assert WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 3 request no'), FailureHandling.STOP_ON_FAILURE).contains(
    'LBR-' + requestID)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 4'), 0)

assert WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 4 request no'), FailureHandling.STOP_ON_FAILURE).contains(
    'MUNI-' + requestID)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 5'), 0)

assert WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 5 request no'), FailureHandling.STOP_ON_FAILURE).contains(
    'TACS-' + requestID)

WebUI.click(findTestObject('Page_foi.flow/queue/div_queue header CURRENT STATE'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-edu-options'), [('requestID') : requestID], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-jer-options'), [('requestID') : requestID], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-mma-options'), [('requestID') : requestID], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-tac-options'), [('requestID') : requestID], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-lbr-options'), [('requestID') : requestID], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('divisional tracking/foi-test-divisional-tracking-comments'), [('requestID') : requestID], 
    FailureHandling.STOP_ON_FAILURE)

