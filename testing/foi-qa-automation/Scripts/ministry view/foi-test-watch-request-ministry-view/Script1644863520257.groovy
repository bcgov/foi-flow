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

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/watch/div_add other watchers'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Flex Team'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Intake Team'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_EDU Ministry Team'), 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_close dropdown'))

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            8), ('username') : findTestData('Login Credentials').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('null'), 0)

WebUI.verifyElementText(findTestObject('null'), 'Watch')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/i_Watch eye icon'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '0')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/i_Watch user icon'), 0)

WebUI.click(findTestObject('null'))

WebUI.verifyElementText(findTestObject('null'), 'Unwatch')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.refresh()

WebUI.verifyElementText(findTestObject('null'), 'Unwatch')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.click(findTestObject('null'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '0')

WebUI.verifyElementText(findTestObject('null'), 'Watch')

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '0')

WebUI.verifyElementText(findTestObject('null'), 'Watch')

WebUI.verifyElementText(findTestObject('null'), 'Watch')

WebUI.click(findTestObject('Page_foi.flow/form/watch/div_add other watchers'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/div_watch dropdown popup'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Intake Team'), 0)

//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Processing Team'), 0)
WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Flex Team'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_EDU Ministry Team'), 0)

WebUI.verifyElementNotHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate]), 
    'aria-selected', 0, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate]), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate]), 
    'aria-selected', 'true', 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.verifyElementNotHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + 
            ', ') + firstname]), 'aria-selected', 0, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + 
            firstname]), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + 
            ', ') + firstname]), 'aria-selected', 'true', 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '2')

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + 
            firstname]), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + 
            ', ') + firstname]), 'aria-selected', 0, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_close dropdown'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/watch/div_watch dropdown popup'), 0)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            9), ('username') : findTestData('Login Credentials').getValue('Username', 9)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_Watching Requests'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.verifyElementText(findTestObject('null'), 'Unwatch')

