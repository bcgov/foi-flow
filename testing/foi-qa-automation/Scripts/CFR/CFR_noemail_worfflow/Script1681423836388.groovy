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
import com.kms.katalon.core.configuration.RunConfiguration as RunConfiguration
import org.openqa.selenium.WebDriver as WebDriver
import com.kms.katalon.core.webui.driver.DriverFactory as DriverFactory
import groovy.json.JsonSlurper as JsonSlurper

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            1), ('username') : findTestData('Login Credentials').getValue('Username', 1)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/button_Add Request'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_Flex, Intake'))

Random random = new Random()

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_AXIS ID Number'), 'ABC-2099-' + random.nextInt(10000000 //generate random axis number for sake of test
        ))

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant First Name_MuiInputBase'), 'Firstname')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Last Name_MuiInputBase'), 'Lastname')

//WebUI.setText(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Email_MuiInputBase'), 'a@b.ca')
WebUI.click(findTestObject('Page_foi.flow/form/inputs/applicant details/div_Category'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Individual'))

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Street Address_outlined-streetAddress'), '2210 Sooke Rd')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Secondary Street Address'), '1')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_City_outlined-city'), 'Victoria')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Province_outlined-province'), 'BC')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Country'), 'Canada')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Postal Code'), 'V9B0E3')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Home Phone_outlined-homePhone'), '6041234567')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description'), 'testing 123 description')

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description'), 0)

//WebUI.scrollToPosition(0, 0)
//WebUI.scrollToElement(findTestObject('null'), 0)
//WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request description/span_EDU_selectspanEDU'), 0)
//WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request description/span_EDU_checkmark'), 0)
WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_EDU_selectspanEDU'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

//WebUI.takeScreenshotAsCheckpoint('current_viewport')
WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request details/input_Start Date'), '2021-12-16')

WebUI.waitForElementClickable(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date_receivedDate'), 
    0)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date_receivedDate'), '2021-12-16')

//WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date_receivedDate'), '2023-02-23')
WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/request type options/li_general'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description'), 0)

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'), 
        'color'), 'rgba(255, 0, 0, 1)', false)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'))

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'), 
        'color'), 'rgba(0, 0, 0, 0.87)', false)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Mode'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Mode'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/received mode options/li_Email'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Delivery Mode'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/delivery mode options/li_Secure File Transfer'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'))

WebUI.delay(5)

//WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)
requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Fee Estimate'), 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

//WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'))
WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

//WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))
WebDriver IAOuser = DriverFactory.getWebDriver()

WebDriver ministryUser = CustomKeywords.'browser.newWindow.open'()

DriverFactory.changeWebDriver(ministryUser)

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            8), ('username') : findTestData('Login Credentials').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/div_ministry assigned to'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee foiedu, foiedu'))

WebUI.click(findTestObject('Page_foi.flow/form/watch/div_add other watchers'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_foiedu2, foiedu2'))

//WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_close dropdown'))
//def ldd=WebUI.(findTestObject('Page_foi.flow/queue/div_queue header LDD'))
//WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)
WebUI.delay(3)

WebUI.refresh()

WebUI.click(findTestObject('CFR/div_CFR Form'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Actual Hours_locating'))

//WebUI.click(findTestObject('CFR/input_Estimated Hours_locating'))
WebUI.verifyElementAttributeValue(findTestObject('CFR/input_Estimated Hours_locating'), 'step', '0.25', 0)

WebUI.verifyElementVisible(findTestObject('CFR/input_Actual Hours_producing'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Actual Hours IAO_iaoPreparing'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Estimated Hours_locating'))

WebUI.verifyElementClickable(findTestObject('CFR/input_Estimated Hours_locating'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Estimated Hours_producing'))

WebUI.verifyElementClickable(findTestObject('CFR/input_Estimated Hours_producing'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Hardcopy Estimated Pages_hardcopyPages'))

WebUI.verifyElementClickable(findTestObject('CFR/input_Hardcopy Estimated Pages_hardcopyPages'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Actual Hours IAO_iaoPreparing'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Fee Waiver Amount_feewaiverAmount'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Refund Amount_refundAmount'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Amount Paid_amountPaid'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Balance Remaining_balanceRemaining'))

WebUI.verifyElementClickable(findTestObject('CFR/input_Estimated Hours Ministry_ministryPreparing'))

WebUI.verifyElementVisible(findTestObject('CFR/textarea_Combined suggestions for futher clarifications_suggestions'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Fee Estimate'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'))

WebUI.setText(findTestObject('CFR/input_Estimated Hours_locating'), '5')

WebUI.setText(findTestObject('CFR/input_Estimated Hours_producing'), '3')

WebUI.setText(findTestObject('CFR/input_Estimated Hours Ministry_ministryPreparing'), '7')

WebUI.setText(findTestObject('CFR/input_Hardcopy Estimated Pages_hardcopyPages'), '5')

WebUI.setText(findTestObject('CFR/textarea_Combined suggestions for futher clarifications_suggestions'), 'verified')

WebUI.scrollToElement(findTestObject('CFR/div_270.8'), 0)

WebUI.verifyElementText(findTestObject('CFR/div_270.8'), '$360.5')

WebUI.delay(3)

WebUI.scrollToElement(findTestObject('CFR/button_Save'), 0)

WebUI.click(findTestObject('CFR/button_Save'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'))

WebUI.delay(4)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Fee Estimate'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

DriverFactory.changeWebDriver(IAOuser)

WebUI.refresh()

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Fee Estimate', 
    0)

WebUI.verifyElementPresent(findTestObject('CFR/div_Contact Applicant'), 0)

WebUI.click(findTestObject('CFR/div_CFR Form'))

WebUI.scrollToPosition(1141, 60)

WebUI.click(findTestObject('CFR/CFR_status/div_Approved'))

WebUI.click(findTestObject('CFR/CFR_status/li_Needs Clarification with Ministry'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

DriverFactory.changeWebDriver(ministryUser)

WebUI.refresh()

WebUI.click(findTestObject('CFR/div_CFR Form'))

WebUI.scrollToPosition(1141, 60)

WebUI.click(findTestObject('CFR/CFR_status/div_Approved'))

WebUI.click(findTestObject('CFR/CFR_status/li_In Review with IAO'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

DriverFactory.changeWebDriver(IAOuser)

WebUI.refresh()

WebUI.click(findTestObject('CFR/div_CFR Form'))

WebUI.setText(findTestObject('CFR/input_Estimated Hours IAO_iaoPreparing'), '1')

WebUI.verifyElementText(findTestObject('CFR/span_300.8'), '$390.5')

WebUI.scrollToElement(findTestObject('CFR/button_Save'), 0)

//WebUI.click(findTestObject('Object Repository/CFR/Page_ABC-700-602/p_hr(s)'))
WebUI.click(findTestObject('CFR/button_Save'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_On Hold'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'))

WebUI.refresh()

WebUI.click(findTestObject('CFR/div_CFR Form'))

WebUI.scrollToPosition(1141, 60)

WebUI.click(findTestObject('CFR/CFR_status/div_Approved'))

WebUI.click(findTestObject('CFR/CFR_status/li_Approved'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_On Hold'))

WebUI.delay(4)

WebUI.verifyElementVisible(findTestObject('CFR/Email_missing/span_I foiintakeidir have completed placed applicant processing fees letter in outbox to be mailed'))

if (WebUI.verifyElementPresent(findTestObject('CFR/Email_missing/span_I foiintakeidir have completed placed applicant processing fees letter in outbox to be mailed'), 
    1, FailureHandling.OPTIONAL)) {
    WebUI.click(findTestObject('CFR/Email_missing/span_I foiintakeidir have completed placed applicant processing fees letter in outbox to be mailed'))
}

if (WebUI.verifyElementPresent(findTestObject('CFR/Email_missing/span_I foiintakeidir have completed placed applicant processing fees letter in outbox to be mailed'), 
    1, FailureHandling.OPTIONAL)) {
    WebUI.click(findTestObject('CFR/Email_missing/button_Cancel'))
}

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Full Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

ministryUser.close()

IAOuser.close()

