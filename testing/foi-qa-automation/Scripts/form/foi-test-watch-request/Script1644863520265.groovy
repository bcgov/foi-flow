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

def requestID = WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : GlobalVariable.password
        , ('username') : GlobalVariable.username, ('firstname') : GlobalVariable.firstname, ('lastname') : GlobalVariable.lastname
        , ('applicantFirstname') : '', ('applicantLastname') : '', ('category') : '', ('email') : findTestData('Sample Applicant').getValue(
            'email', 1), ('streetAddress') : findTestData('Sample Applicant').getValue('streetAddress', 1), ('streetAddress2') : findTestData(
            'Sample Applicant').getValue('streetAddress2', 1), ('city') : findTestData('Sample Applicant').getValue('city', 
            1), ('province') : findTestData('Sample Applicant').getValue('province', 1), ('country') : findTestData('Sample Applicant').getValue(
            'country', 1), ('postalCode') : findTestData('Sample Applicant').getValue('postalCode', 1), ('homePhone') : findTestData(
            'Sample Applicant').getValue('homePhone', 1), ('description') : findTestData('Sample Applicant').getValue('description', 
            1), ('startDate') : '', ('receivedDate') : '', ('receivedMode') : '', ('requestType') : '', ('deliveryMode') : ''
        , ('sendRequest') : true, ('variable') : ''], FailureHandling.STOP_ON_FAILURE)

WebUI.refresh()

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/button_Watch'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Watch')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/i_Watch eye icon'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '0')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/i_Watch user icon'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/watch/button_Unwatch'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Unwatch'), 'Unwatch')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Unwatch'), 'Unwatch')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.click(findTestObject('Page_foi.flow/form/watch/button_Unwatch'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '0')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Watch')

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '0')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Watch')

WebUI.click(findTestObject('Page_foi.flow/form/watch/div_add other watchers'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/div_watch dropdown popup'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Intake Team'), 0)

//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Business Team'), 0)
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Central Team'), 0)
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_MCFD Personals Team'), 0)
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Social Education'), 0)
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Resource Team'), 0)
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Business Team'), 0)
//
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Processing Team'), 0)
WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Flex Team'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_EDU Ministry Team'), 
    0)

WebUI.verifyElementNotHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate]), 
    'aria-selected', 0, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate]))

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate]), 
    'aria-selected', 'true', 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + 
            ', ') + firstname]), 'aria-selected', 0, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_Flex, foiIntake'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '2')

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + 
            ', ') + firstname]), 'aria-selected', 'true', 0)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + 
            firstname]), FailureHandling.STOP_ON_FAILURE)

//WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + 
//           ', ') + firstname]), 'aria-selected', 'true', 0, FailureHandling.STOP_ON_FAILURE)
WebUI.refresh(FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/watch/div_watch dropdown popup'), 0)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            6), ('username') : findTestData('Login Credentials').getValue('Username', 6)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_Watching Requests'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), 'U-00' + requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 request no'), 'EDU-2099-' + requestID)

//WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 request no'), 'U-00' + requestID) // put this line back in and remove previous line after axis phase out
WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Watch')

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            1), ('username') : findTestData('Login Credentials').getValue('Username', 1)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_Watching Requests'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), 'U-00' + requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.closeBrowser()

