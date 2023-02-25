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

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.callTestCase(findTestCase('helper/foi-test-verify-next-assignee'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/state change dialog/span_State Change Dialog message'), ('Are you sure you want to change Request #' + 
    WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)) + ' to Call For Records?')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/state change dialog/td_Minstry Next Assignee'), 'Ministry of Education and Childcare Queue')

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Open', 
    0)

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

//WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/h4_CFR Due in 10 Days'), 'CFR Due in 10 Days')
WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments (3)')

WebUI.click(findTestObject('Page_foi.flow/comment/Page_ABC-2099-50/span_All'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 2 text'), ((firstname + ' ') + lastname) + 
    ' changed the state of the request to Call For Records')

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Call For Records', 
    0)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            8), ('username') : findTestData('Login Credentials').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header ID NUMBER'), 0)
//
//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header APPLICANT TYPE'), 0)
//
//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header REQUEST TYPE'), 0)
//
//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header CURRENT STATE'), 0)
//
//WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/queue/div_queue header CURRENT STATE'), 'aria-sort', 'ascending', 
//    0)
//
//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header ASSIGNED TO'), 0)
//
//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header RECORDS DUE'), 0)
//
//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header LDD'), 0)
WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

assert WebUI.getText(findTestObject('Page_foi.flow/queue/div_request queue row 1 type')).toLowerCase() == findTestData('Sample Applicant').getValue(
    'requestType', 1)

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 category'), category)

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 'background-color'), 
    'rgba(207, 215, 227, 1)', false)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

//WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/h4_CFR Due in 10 Days'), 'CFR Due in 10 Days')
WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/div_request form ministry APPLICANT DETAILS'), 
    0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/label_APPLICANT DETAILS'), 'Applicant Details')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/div_request from ministry REQUEST DESCRIPTION'), 
    0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/label_REQUEST DESCRIPTION'), 'REQUEST DESCRIPTION')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/div_request form ministry REQUEST DETAILS'), 
    0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/label_REQUEST DETAILS'), 'REQUEST DETAILS')

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/b_ministry form Application Type'), 'Application Type')

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/span_ministry form Category'), category)

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/b_ministry form Request Type'), 'Request Type')

assert WebUI.getText(findTestObject('Page_foi.flow/ministry view/form/span_ministry form request type')).toLowerCase() == 
findTestData('Sample Applicant').getValue('requestType', 1)

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/b_ministry form Authorization'), 'Authorization')

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/b_ministry form Start Date'), 'Start Date:')

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/b_ministry form End Date'), 'End Date:')

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/b_ministry form Request Description'), 'Request Description')

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/p_ministry form request description'), 'testing 123 description')

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/b_ministry form Selected Ministry Ministry of Education'), 
    'Selected Ministry: Ministry of Education and Childcare')

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/b_ministry form Request Opened'), 'Request Opened')

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/b_ministry form Records Due Date'), 'Records Due Date')

WebUI.verifyElementText(findTestObject('Page_foi.flow/ministry view/form/b_ministry form Legislated Due Date'), 'Legislated Due Date')

