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
import groovy.json.JsonSlurper as JsonSlurper
import static com.kms.katalon.core.checkpoint.CheckpointFactory.findCheckpoint

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

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'))

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            9), ('username') : findTestData('Login Credentials').getValue('Username', 9)], FailureHandling.STOP_ON_FAILURE)

//WebUI.click(findTestObject('Page_foi.flow/queue/div_Watching Requests'))
//WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))
//WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)
WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.refresh()

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/div_ministry assigned to'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee foiedu, foiedu'))

//def ldd=WebUI.(findTestObject('Page_foi.flow/queue/div_queue header LDD'))
WebUI.delay(3, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            1), ('username') : findTestData('Login Credentials').getValue('Username', 1)], FailureHandling.STOP_ON_FAILURE)

//WebUI.click(findTestObject('Page_foi.flow/queue/div_Watching Requests'))
//WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))
//WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)
WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Object Repository/Extension/button_New Extension'))

WebUI.click(findTestObject('Object Repository/Extension/body_FOI  Intake Flex 0Sign OutABC-2099-322_22de9c'))

WebUI.click(findTestObject('Extension/li_OIPC - Large Volume andor Volume of Search'))

WebUI.setText(findTestObject('Object Repository/Extension/input_Extended Due Days_numberDays'), '6')

WebUI.verifyElementVisible(findTestObject('Object Repository/Extension/button_Save'))

WebUI.click(findTestObject('Object Repository/Extension/button_Save'))

//WebUI.click(findTestObject('Extension/svg_Pending_MuiSvgIcon-root'))
//WebUI.click(findTestObject('Extension/li_Edit'))
//WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)
//WebUI.click(findTestObject('Extension/Extension_Denial/svg_Approved_MuiSvgIcon-root'))
//WebUI.delay(5)
//WebUI.scrollToElement(findTestObject('Extension/button_Add Files (2)'), 0)
//WebUI.click(findTestObject('Extension/button_Add Files (2)'))
//WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
//    '/Test Attachments/test2.docx')
//WebUI.delay(5)
//WebUI.verifyElementVisible(findTestObject('Object Repository/Extension/button_Save'))
//WebUI.verifyElementClickable(findTestObject('Extension/button_Save'))
//WebUI.click(findTestObject('Extension/Extension_Denial/button_Save'))
WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('Extensions/foi-test-extension-with-attachment'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.refresh()

WebUI.delay(5)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Object Repository/Extension/span_Request History Comments'))

WebUI.click(findTestObject('Page_foi.flow/comment/span_User Comments'))

WebUI.click(findTestObject('Object Repository/Extension/span_Request History Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'The OIPC has denied a 6 day extension.')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Attachments'))

WebUI.click(findTestObject('Extension/span_ALL'))

WebUI.verifyElementText(findTestObject('Extension/div_Extension OIPC - Approved.docx'), 'test2.docx')

WebUI.verifyElementText(findTestObject('Extension/span_Extension - Approved'), 'Extension - Denied')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'))

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_Closing Reason'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/dropdown options/li_Partial Disclosure'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.closeBrowser()

