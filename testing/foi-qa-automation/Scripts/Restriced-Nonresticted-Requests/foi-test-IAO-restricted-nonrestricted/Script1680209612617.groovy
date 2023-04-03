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

WebUI.verifyElementClickable(findTestObject('Restricted_Requests/div_Unrestricted'))

WebUI.click(findTestObject('Restricted_Requests/div_Unrestricted'))

WebUI.verifyElementAttributeValue(findTestObject('Restricted_Requests/li_Unrestricted'), 'aria-disabled', 'true', 0)

WebUI.click(findTestObject('Restricted_Requests/li_Restricted'))

WebUI.click(findTestObject('Restricted_Requests/button_Cancel'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_Flex, Intake'))

WebUI.click(findTestObject('Restricted_Requests/div_Unrestricted'))

WebUI.click(findTestObject('Restricted_Requests/li_Restricted'))

WebUI.verifyElementPresent(findTestObject('Restricted_Requests/Change_to restricted/button_Save Change'), 0)

WebUI.verifyElementPresent(findTestObject('Restricted_Requests/button_Cancel'), 0)

WebUI.click(findTestObject('Restricted_Requests/button_Cancel'))

WebUI.click(findTestObject('Restricted_Requests/div_Unrestricted'))

WebUI.click(findTestObject('Restricted_Requests/li_Restricted'))

WebUI.click(findTestObject('Restricted_Requests/Change_to restricted/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/watch/div_add other watchers'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/input_User, foiSuper_Intake Teamfoisuperidir'))

WebUI.click(findTestObject('Restricted_Requests/Change_to restricted/Change_watcher_restricted/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_close dropdown'))

//WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)
WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/li_Flex Team'), 'aria-disabled', 
    'true', 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/li_Central Team'), 'aria-disabled', 
    'true', 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/li_MCFD Personals Team'), 'aria-disabled', 
    'true', 0)

WebUI.delay(4)

WebUI.refresh()

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment tagging popup'), 0)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), '@')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Tagging option 1'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Tagging option 2'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Tagging option 3'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Tagging option 4'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/div_Tagging option 2'))

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'm')

WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.verifyElementPresent(findTestObject('Restricted_Requests/div_Flex, Intake_foi-dashboard-restricted MuiDataGrid-cell--withRenderer MuiDataGrid-cell MuiDataGrid-cell--textLeft'), 
    0)

WebUI.verifyElementText(findTestObject('Restricted_Requests/div_Restricted, Request'), 'Restricted, Request')

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            4), ('username') : findTestData('Login Credentials').getValue('Username', 4)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(3)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

//WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.click(findTestObject('Page_foi.flow/queue/div_Watching Requests'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Restricted_Requests/div_Restricted'))

WebUI.click(findTestObject('Restricted_Requests/li_Unrestricted'))

WebUI.verifyElementText(findTestObject('Restricted_Requests/div_Only the Intake Manager can remove the restricted flag on a request'), 
    'Only the Intake Manager can remove the restricted flag on a request')

WebUI.verifyElementHasAttribute(findTestObject('Restricted_Requests/Change_to restricted/Change_watcher_restricted/button_Save Change'), 
    'disabled', 0)

WebUI.verifyElementPresent(findTestObject('Restricted_Requests/button_Cancel'), 0)

WebUI.click(findTestObject('Restricted_Requests/button_Cancel'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Page_foi.flow/comment/span_Request History Comments'))

WebUI.delay(3)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), ((((findTestData('Login Credentials').getValue(
        'First Name', 1) + ' ') + findTestData('Login Credentials').getValue('Last Name', 1)) + ' has made ') + (((findTestData(
        'Login Credentials').getValue('Last Name', 4) + ', ') + findTestData('Login Credentials').getValue('First Name', 
        4)) + ' ')) + 'a watcher')

WebUI.click(findTestObject('Page_foi.flow/comment/span_User Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), ((findTestData('Login Credentials').getValue(
        'Last Name', 4) + ', ') + findTestData('Login Credentials').getValue('First Name', 4)) + ' m')
WebUI.refresh()

WebUI.clickOffset(findTestObject('Page_foi.flow/navbar/notification/notification bell'), -2, 4)



WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 request id'), requestID)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 message'), 'You\'ve been tagged in a comment:')

WebUI.clickOffset(findTestObject('Page_foi.flow/navbar/notification/notification bell'), -2, 4)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            1), ('username') : findTestData('Login Credentials').getValue('Username', 1)], FailureHandling.STOP_ON_FAILURE)

//WebUI.click(findTestObject('Page_foi.flow/queue/div_My Requests'))
WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/watch/div_add other watchers'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/input_User, foiSuper_Intake Teamfoisuperidir'))

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Page_foi.flow/comment/span_Request History Comments'))

WebUI.delay(3)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), ((((findTestData('Login Credentials').getValue(
        'First Name', 1) + ' ') + findTestData('Login Credentials').getValue('Last Name', 1)) + ' has removed ') + (((findTestData(
        'Login Credentials').getValue('Last Name', 4) + ', ') + findTestData('Login Credentials').getValue('First Name', 
        4)) + ' ')) + 'as a watcher')

WebUI.closeBrowser()

