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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : findTestData('Login Credentials').getValue(
            'Password', 1), ('username') : findTestData('Login Credentials').getValue('Username', 1), ('firstname') : findTestData(
            'Login Credentials').getValue('First Name', 1), ('lastname') : findTestData('Login Credentials').getValue('Last Name', 
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

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

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

//def ldd=WebUI.(findTestObject('Page_foi.flow/queue/div_queue header LDD'))
WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.refresh()

WebUI.click(findTestObject('CFR/div_CFR Form'))

WebUI.verifyElementVisible(findTestObject('CFR/input_Actual Hours_locating'))

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

WebUI.setText(findTestObject('CFR/input_Estimated Hours_locating'), '5')

WebUI.setText(findTestObject('CFR/input_Estimated Hours_producing'), '3')

WebUI.setText(findTestObject('CFR/input_Estimated Hours Ministry_ministryPreparing'), '4')

WebUI.setText(findTestObject('CFR/input_Hardcopy Estimated Pages_hardcopyPages'), '8')

WebUI.setText(findTestObject('CFR/textarea_Combined suggestions for futher clarifications_suggestions'), 'verified')

WebUI.scrollToElement(findTestObject('CFR/div_270.8'), 0)

WebUI.verifyElementText(findTestObject('CFR/div_270.8'), '$270.8')

WebUI.delay(3)

WebUI.scrollToElement(findTestObject('CFR/button_Save'), 0)

WebUI.click(findTestObject('CFR/button_Save'))

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

//WebUI.scrollToElement(findTestObject('CFR/CFR_status/div_idapp'), 0)
WebUI.delay(3)

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

WebUI.delay(6)

WebUI.verifyElementNotClickable(findTestObject('CFR/NewCFR/button_Create New CFR Form'))

DriverFactory.changeWebDriver(IAOuser)

WebUI.refresh()

WebUI.click(findTestObject('CFR/div_CFR Form'))

WebUI.setText(findTestObject('CFR/input_Estimated Hours IAO_iaoPreparing'), '1')

WebUI.verifyElementText(findTestObject('CFR/span_300.8'), '$300.8')

WebUI.scrollToElement(findTestObject('CFR/button_Save'), 0)

//WebUI.click(findTestObject('Object Repository/CFR/Page_ABC-700-602/p_hr(s)'))
WebUI.click(findTestObject('CFR/button_Save'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_On Hold'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'))

WebUI.refresh(FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('CFR/div_CFR Form'))

WebUI.scrollToPosition(1141, 60)

WebUI.click(findTestObject('CFR/CFR_status/div_Approved'))

WebUI.click(findTestObject('CFR/CFR_status/li_Approved'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

DriverFactory.changeWebDriver(ministryUser)

WebUI.refresh()

WebUI.click(findTestObject('CFR/div_CFR Form'))

WebUI.click(findTestObject('CFR/NewCFR/button_Create New CFR Form'))

WebUI.click(findTestObject('CFR/NewCFR/button_Continue'))

WebUI.setText(findTestObject('CFR/input_Estimated Hours_locating'), '5')

WebUI.setText(findTestObject('CFR/input_Estimated Hours_producing'), '3')

WebUI.scrollToElement(findTestObject('CFR/CFR_status/div_Select CFR Form Status'), 0)

WebUI.click(findTestObject('CFR/NewCFR/div_Select Reason'))

WebUI.click(findTestObject('CFR/NewCFR/li_Revised Fee Estimate'))

WebUI.scrollToElement(findTestObject('CFR/button_Save'), 0)

WebUI.click(findTestObject('CFR/button_Save'))

WebUI.refresh()

WebUI.click(findTestObject('CFR/div_CFR Form'))

WebUI.delay(3)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.refresh()

WebUI.click(findTestObject('CFR/div_CFR Form'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('CFR/NewCFR/button_CFR Form History'))

WebUI.click(findTestObject('CFR/NewCFR/p_CFR Form - Version 1 - Original'))

WebUI.delay(3)

WebUI.verifyElementText(findTestObject('CFR/CFR_Addcorrespondence/p_CFR Form - Version 1 - Original'), 'CFR Form - Version 1 - Original')

WebUI.verifyElementText(findTestObject('CFR/span_300.80'), '$300.80')

WebUI.click(findTestObject('CFR/NewCFR/svg_Close_MuiSvgIcon-root'))

DriverFactory.changeWebDriver(IAOuser)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Full Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

ministryUser.close()

IAOuser.close()

