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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : GlobalVariable.password, ('username') : GlobalVariable.username
        , ('firstname') : GlobalVariable.firstname, ('lastname') : GlobalVariable.lastname, ('applicantFirstname') : '', ('applicantLastname') : ''
        , ('category') : '', ('email') : findTestData('Sample Applicant').getValue('email', 1), ('streetAddress') : findTestData(
            'Sample Applicant').getValue('streetAddress', 1), ('streetAddress2') : findTestData('Sample Applicant').getValue(
            'streetAddress2', 1), ('city') : findTestData('Sample Applicant').getValue('city', 1), ('province') : findTestData(
            'Sample Applicant').getValue('province', 1), ('country') : findTestData('Sample Applicant').getValue('country', 
            1), ('postalCode') : findTestData('Sample Applicant').getValue('postalCode', 1), ('homePhone') : findTestData(
            'Sample Applicant').getValue('homePhone', 1), ('description') : findTestData('Sample Applicant').getValue('description', 
            1), ('startDate') : '', ('receivedDate') : '', ('receivedMode') : '', ('requestType') : '', ('deliveryMode') : ''], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/watch/div_add other watchers'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_User, Super'))

WebUI.click(findTestObject('Page_foi.flow/form/h3_Form Request Title'))

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(3)

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/Page_EDU-2023-1037/li_Peer Review'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/Page_EDU-2023-1037/li_App Fee Owing'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Redirect'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/Page_EDU-2023-1037/li_Peer Review'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Peer Review', 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments (2)')

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            4), ('username') : findTestData('Login Credentials').getValue('Username', 4)], FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.clickOffset(findTestObject('Page_foi.flow/navbar/notification/notification bell'), -2, 4)

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/a_Watching Notifications'))

//WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_watching notification list 1 request id'), 
//  requestID)
WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_watching notification list 1 message'), 'Moved to Peer Review State')

WebUI.clickOffset(findTestObject('Page_foi.flow/navbar/notification/notification bell'), -2, 4)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            1), ('username') : findTestData('Login Credentials').getValue('Username', 1)], FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments (3)')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments (4)')

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            1), ('username') : findTestData('Login Credentials').getValue('Username', 1)], FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/div_ministry assigned to'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee foiedu, foiedu'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Records Review'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Records Review', 
    0)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            1), ('username') : findTestData('Login Credentials').getValue('Username', 1)], FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Consult'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Ministry Sign Off'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/Page_EDU-2023-1037/li_Peer Review'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Response'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/Page_EDU-2023-1037/li_App Fee Owing'), 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Consult'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Records Review'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Ministry Sign Off'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/Page_EDU-2023-1037/li_Peer Review'), 
    0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Response'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Closed', 
    0)

WebUI.closeBrowser()

