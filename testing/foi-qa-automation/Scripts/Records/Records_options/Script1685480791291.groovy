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
import org.openqa.selenium.WebDriver as WebDriver
import com.kms.katalon.core.configuration.RunConfiguration as RunConfiguration
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

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee foiedu, foiedu'))

WebUI.delay(3)

WebUI.refresh()

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division dropdown'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/li_Deputy Ministers Office'), 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Records/input_Select Division Stage_mui-53'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Clarification'), 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/button_Add division to track'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Records/input_Select Division_mui-137'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/li_Ministers Office'), 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Records/input_Select Division Stage_mui-138'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Clarification'), 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Records/div_Records'))

WebUI.delay(4)

WebUI.click(findTestObject('Records/button_Upload Records'))

WebUI.click(findTestObject('Records/button_Add Files'))

println(RunConfiguration.getProjectDir() + '/Test Attachments')

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/Excelattached (1).msg')

WebUI.click(findTestObject('Records/button_Add Files1'))

println(RunConfiguration.getProjectDir() + '/Test Attachments')

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/test.docx')

WebUI.click(findTestObject('Records/button_Add Files1'))

println(RunConfiguration.getProjectDir() + '/Test Attachments')

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/test2.docx')

WebUI.click(findTestObject('Records/button_Add Files1'))

println(RunConfiguration.getProjectDir() + '/Test Attachments')

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/corrupted.pdf')

WebUI.click(findTestObject('Records/button_Add Files1'))

println(RunConfiguration.getProjectDir() + '/Test Attachments')

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/50mb.pdf')

WebUI.click(findTestObject('Records/span_DEPUTY MINISTERS OFFICE'))

WebUI.click(findTestObject('Records/button_Continue'))

WebUI.delay(100)

WebUI.refresh()

WebUI.delay(8)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Page_foi.flow/comment/span_Request History Comments'))

//WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 2 text'), 'records for harms are ready for export')
WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'A batch of records has been uploaded by foiedu, foiedu')

WebUI.clickOffset(findTestObject('Page_foi.flow/navbar/notification/notification bell'), -2, 4)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1'), 0)

//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 2'), 0)
//WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 message'), 'Records for harms are ready for export')
WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 request id'), requestID)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 message'), 'A batch of records has been uploaded by foiedu, foiedu')

WebUI.clickOffset(findTestObject('Page_foi.flow/navbar/notification/notification bell'), -2, 4)

WebUI.refresh()

WebUI.click(findTestObject('Records/div_Records'))

WebUI.click(findTestObject('Records/div_ (1)'))

WebUI.click(findTestObject('Records/li_Download for Harms (1)'))

WebUI.delay(8)

WebUI.click(findTestObject('Records/button_Remove Attachments'))

WebUI.verifyElementClickable(findTestObject('Records/button_Continue (1)'))

WebUI.verifyElementClickable(findTestObject('Records/svg_Close_MuiSvgIcon-root'))

WebUI.verifyElementClickable(findTestObject('Records/button_Continue (1)'))

WebUI.verifyElementPresent(findTestObject('Records/span_Are you sure you want to delete the attachments from this request This will remove all attachments from the redaction app'), 
    0)

WebUI.verifyElementText(findTestObject('Records/span_Are you sure you want to delete the attachments from this request This will remove all attachments from the redaction app'), 
    'Are you sure you want to delete the attachments from this request?\nThis will remove all attachments from the redaction app.')

WebUI.click(findTestObject('Records/button_Continue (1)'))

WebUI.delay(8)

WebUI.verifyElementNotPresent(findTestObject('Records/span_budget-2018-tables-appendix.xlsx'), 0)

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Page_foi.flow/comment/span_Request History Comments'))

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), '50mb.pdf file(s) could not be added to package, please check record for errors')

WebUI.clickOffset(findTestObject('Page_foi.flow/navbar/notification/notification bell'), -2, 4)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 request id'), requestID)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 message'), '50mb.pdf file(s) could not be added to package, please check record for errors')

WebUI.clickOffset(findTestObject('Page_foi.flow/navbar/notification/notification bell'), -2, 4)

WebUI.click(findTestObject('Records/div_Records'))

WebUI.click(findTestObject('Records/svg_Error duringdeduplication_MuiSvgIcon-root'))

WebUI.click(findTestObject('Records/li_Re-Try'))

WebUI.delay(3)

//WebUI.verifyElementPresent(findTestObject('Records/svg_INCOMPATIBLE_svg-inline--fa fa-spinner fa-w-16 fa-2x jss60'), 
//    0, FailureHandling.STOP_ON_FAILURE)
WebUI.refresh()

WebUI.click(findTestObject('Records/div_Records'))

WebUI.click(findTestObject('Records/svg_Error duringdeduplication_MuiSvgIcon-root'))

WebUI.delay(8)

WebUI.click(findTestObject('Records/li_Replace Manually (1)'))

WebUI.click(findTestObject('Records/button_Add Files1'))

println(RunConfiguration.getProjectDir() + '/Test Attachments')

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/sample.pdf')

WebUI.click(findTestObject('Page_Log in to FOI/button_Continue'))

WebUI.delay(30)

WebUI.refresh()

WebUI.click(findTestObject('Records/div_Records'))

WebUI.click(findTestObject('Records/svg_Error duringdeduplication_MuiSvgIcon-root'))

WebUI.verifyElementPresent(findTestObject('Records/options_converted_file/li_Download Replaced'), 0)

WebUI.verifyElementPresent(findTestObject('Records/options_converted_file/li_Download Original'), 0)

WebUI.verifyElementPresent(findTestObject('Records/li_Replace Manually (1)'), 0)

WebUI.click(findTestObject('Records/li_Delete (1)'))

WebUI.click(findTestObject('Page_Log in to FOI/button_Continue'))

WebUI.delay(30)

WebUI.verifyElementNotPresent(findTestObject('Records/span_sample.pdf'), 0)

//WebUI.verifyElementPresent(findTestObject('Records/svg_foiedu, foiedu_svg-inline--fa fa-clone fa-w-16 fa-2x jss60 (1)'), 
//   0)
DriverFactory.changeWebDriver(IAOuser)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

ministryUser.close()

IAOuser.close()

