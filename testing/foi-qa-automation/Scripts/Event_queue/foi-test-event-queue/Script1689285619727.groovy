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
            'Password', 6), ('username') : findTestData('Login Credentials').getValue('Username', 6), ('firstname') : findTestData(
            'Login Credentials').getValue('First Name', 6), ('lastname') : findTestData('Login Credentials').getValue('Last Name', 
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

WebUI.delay(5)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/div_ministry assigned to'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee foiedu, foiedu'))

WebUI.delay(3)

WebUI.refresh()

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.delay(3)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division dropdown'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/li_Deputy Ministers Office'), 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Records/input_Select Division Stage_mui-53'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Clarification'), 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/button_Add division to track'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division dropdown row 2'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/li_Ministers Office'), 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Records/input_Select Division Stage_mui-55'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Clarification'), 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Records/div_Records'))

WebUI.delay(4)

WebUI.click(findTestObject('Records/button_Upload Records'))

WebUI.click(findTestObject('Records/button_Add Files'))

println(RunConfiguration.getProjectDir() + '/Test Attachments')

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/test.docx')

WebUI.click(findTestObject('Records/span_DEPUTY MINISTERS OFFICE'))

WebUI.click(findTestObject('Records/button_Continue'))

WebUI.delay(40)

WebUI.refresh()

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.click(findTestObject('Event/h3_Event Queue'))

WebUI.verifyElementText(findTestObject('Event/div_foimma, foimma'), 'Foiedu, Foiedu')

def Format1 = 'yyyy-MM-dd'

def today = new Date()

def currentDate = today.format(Format1)

WebUI.verifyElementAttributeValue(findTestObject('Event/svg_DATE  TIME STAMP_MuiSvgIcon-root MuiSvgIcon-fontSizeSmall MuiDataGrid-sortIcon css-1k33q06'), 
    'data-testid', 'ArrowDownwardIcon', 0)

//WebUI.verifyElementText(findTestObject('Event/div_2023 Jul 11  0602 AM'), '')
WebUI.verifyElementText(findTestObject('Event/div_MMA-2023-0953'), requestID)

WebUI.verifyElementText(findTestObject('Event/div_System'), 'Foiedu, Foiedu')

WebUI.verifyElementText(findTestObject('Event/span_Legislative Due Date due'), 'A Batch Of Records Has Be...')

WebUI.click(findTestObject('Event/svg_DATE  TIME STAMP_MuiSvgIcon-root MuiSvgIcon-fontSizeSmall MuiDataGrid-sortIcon css-1k33q06'))

WebUI.verifyElementAttributeValue(findTestObject('Event/svg_DATE  TIME STAMP_MuiSvgIcon-root MuiSvgIcon-fontSizeSmall MuiDataGrid-sortIcon css-1k33q06'), 
    'data-testid', 'ArrowUpwardIcon', 0)

//WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))
DriverFactory.changeWebDriver(IAOuser)

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

//WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
//          1), ('username') : findTestData('Login Credentials').getValue('Username', 1)], FailureHandling.STOP_ON_FAILURE)
WebUI.click(findTestObject('Event/h3_Event Queue'))

WebUI.verifyElementText(findTestObject('Event/div_Intake, FOI'), 'Intake, FOI')

WebUI.verifyElementText(findTestObject('Event/div_foiedu, foiedu'), 'Foiedu, Foiedu')

WebUI.verifyElementAttributeValue(findTestObject('Event/svg_DATE  TIME STAMP_MuiSvgIcon-root MuiSvgIcon-fontSizeSmall MuiDataGrid-sortIcon css-1k33q06'), 
    'data-testid', 'ArrowDownwardIcon', 0)

WebUI.click(findTestObject('Event/div_Intake, FOI'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'test few')

WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.click(findTestObject('Event/h3_Event Queue'))

WebUI.verifyElementText(findTestObject('Event/div_Intake, FOI'), 'Intake, FOI')

WebUI.verifyElementText(findTestObject('Event/foi_edu'), 'Foiedu, Foiedu')

WebUI.verifyElementText(findTestObject('Records/Page_Event Queue/div_EDU-2099-21878'), requestID)

WebUI.verifyElementText(findTestObject('Records/Page_Event Queue/div_test few'), 'Test Few')

WebUI.click(findTestObject('Records/Page_Event Queue/div_test few'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'test few')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'))

WebUI.click(findTestObject('Page_foi.flow/form/watch/div_add other watchers'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Event/li_User, Super'))

WebUI.refresh()

WebUI.delay(6)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            4), ('username') : findTestData('Login Credentials').getValue('Username', 4)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Event/h3_Event Queue'))

WebUI.click(findTestObject('Event/span_WATCHING REQUESTS'))

WebUI.verifyElementText(findTestObject('Records/Page_Event Queue/div_EDU-2099-21878'), requestID)

WebUI.verifyElementText(findTestObject('Records/Page_Event Queue/div_test few'), 'Test Few')

WebUI.click(findTestObject('Event/svg_DATE  TIME STAMP_MuiSvgIcon-root MuiSvgIcon-fontSizeSmall MuiDataGrid-sortIcon css-1k33q06'))

WebUI.verifyElementAttributeValue(findTestObject('Event/svg_DATE  TIME STAMP_MuiSvgIcon-root MuiSvgIcon-fontSizeSmall MuiDataGrid-sortIcon css-1k33q06'), 
    'data-testid', 'ArrowUpwardIcon', 0)

WebUI.verifyElementAttributeValue(findTestObject('Event/Page_Event Queue/select_102050100'), 'value', '100', 0)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            6), ('username') : findTestData('Login Credentials').getValue('Username', 6)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Requests'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.delay(5)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

ministryUser.close()

IAOuser.close()

