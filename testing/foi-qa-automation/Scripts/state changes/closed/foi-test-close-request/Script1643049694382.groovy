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
import org.apache.ivy.core.search.OrganisationEntry as OrganisationEntry
import org.openqa.selenium.Keys as Keys
import org.openqa.selenium.WebDriver as WebDriver
import com.kms.katalon.core.webui.driver.DriverFactory as DriverFactory

def today = new Date()

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [:], FailureHandling.STOP_ON_FAILURE)

println(today.format('HHmm', TimeZone.getTimeZone('Canada/Pacific')).toInteger() > 1630)

if (today.format('HHmm', TimeZone.getTimeZone('Canada/Pacific')).toInteger() > 1630) {
    today = today.next()
}

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebDriver IAOuser = DriverFactory.getWebDriver()

WebDriver ministryUser = CustomKeywords.'browser.newWindow.open'()

DriverFactory.changeWebDriver(ministryUser)

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            8), ('username') : findTestData('Login Credentials').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

DriverFactory.changeWebDriver(IAOuser)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/closing modal/span_Close Request Dialog Applicant'), (applicantFirstname + 
    ' ') + applicantLastname)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/closing modal/span_Close Request Dialog Organization'), organization)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/div_Close Request Fee Waiver'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/div_Close Request Fee Remaining'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/input_Close Request Start Date'), 0)

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/closing modal/input_Close Request Start Date'), 'disabled', 
    0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/closing modal/input_Closing Date'), 'value', today.format(
        'yyyy-MM-dd'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/closing modal/input_Closing Date'), 'max', today.format(
        'yyyy-MM-dd'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'), 0)

WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Abandoned'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Access Denied'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Application Fee - Abandoned'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Full Disclosure'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_No Resp. Records ExistLocated'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Outside Scope of Act'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Records in another MinOrg'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Refuse to Confirm or Deny'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Routinely Releasable'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Section 43'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Transferred'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Withdrawn'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), 'Partial Disclosure')

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Call For Records', 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Closed', 
    0)

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar'), 'background-color'), 'rgba(26, 26, 26, 1)', 
    false)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/Page_ABC-2099-50/span_Request History Comments'))

WebUI.delay(5)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), ((firstname + ' ') + lastname) + 
    ' changed the state of the request to Closed')

ministryUser.close()

IAOuser.close()

