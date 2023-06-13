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

WebUI.click(findTestObject('Extension/button_Cancel'))

WebUI.click(findTestObject('Object Repository/Extension/button_New Extension'))

//WebUI.verifyElementNotVisible(findTestObject('Object Repository/Extension/button_Save'))
WebUI.click(findTestObject('Object Repository/Extension/body_FOI  Intake Flex 0Sign OutABC-2099-322_22de9c'))

WebUI.verifyElementVisible(findTestObject('Extension/li_Public Body - Applicant Consent'))

WebUI.verifyElementVisible(findTestObject('Extension/li_Public Body - Consultation (1)'))

WebUI.verifyElementVisible(findTestObject('Extension/li_Public Body - Further Detail from Applicant Required'))

WebUI.verifyElementVisible(findTestObject('Extension/li_Public Body - Large Volume andor Volume of Search'))

WebUI.verifyElementVisible(findTestObject('Extension/li_Public Body - Large Volume andor Volume of Search and Consultation'))

WebUI.verifyElementVisible(findTestObject('Extension/li_OIPC - Applicant Consent'))

WebUI.verifyElementVisible(findTestObject('Extension/li_OIPC - Consultation'))

WebUI.verifyElementVisible(findTestObject('Extension/li_OIPC - Further Detail from Applicant Required'))

WebUI.verifyElementVisible(findTestObject('Extension/li_OIPC - Large Volume andor Volume of Search and Consultation'))

WebUI.click(findTestObject('Object Repository/Extension/li_Public Body - Consultation'))

WebUI.delay(5)

WebUI.verifyElementAttributeValue(findTestObject('Extension/input_Extended Due Days_numberDays'), 'value', '30', 0)

WebUI.setText(findTestObject('Object Repository/Extension/input_Extended Due Days_numberDays'), '6')

WebUI.verifyElementVisible(findTestObject('Object Repository/Extension/button_Save'))

WebUI.click(findTestObject('Object Repository/Extension/button_Save'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request details/Page_ABC-2099-7654195/input_Legislated Due Date_dueDate'), 
    0)

def ldd = WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/Page_ABC-2099-7654195/input_Legislated Due Date_dueDate'), 
    'value').toString()

println(ldd)

def mon = ldd.split('-')[1]

//prinln(mon)
def month = ''

if (mon == '01') {
    month = 'Jan'
}

if (mon == '02') {
    month = 'Feb'
}

if (mon == '03') {
    month = 'Mar'
}

if (mon == '04') {
    month = 'Apr'
}

if (mon == '05') {
    month = 'May'
}

if (mon == '06') {
    month = 'Jun'
}

if (mon == '07') {
    month = 'Jul'
}

if (mon == '08') {
    month = 'Aug'
}

if (mon == '09') {
    month = 'Sep'
}

//println(month)
def newldddate1 = Date.parse('yyyy-MM-dd', ldd).format('MM/dd/yyyy')

def newldddate = newldddate1.toString()

def date1 = newldddate.split('/')[1]

def year1 = newldddate.split('/')[2]

WebUI.delay(3)

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Object Repository/Extension/span_Request History Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), (((('Intake Flex has taken a 30 day Public Body extension. The new legislated due date is ' + 
    month) + ' ') + date1) + ' ') + year1)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'))

//
WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Object Repository/Extension/button_New Extension'))

//WebUI.verifyElementNotVisible(findTestObject('Object Repository/Extension/button_Save'))
WebUI.click(findTestObject('Object Repository/Extension/body_FOI  Intake Flex 0Sign OutABC-2099-322_22de9c'))

WebUI.click(findTestObject('Extension/li_OIPC - Large Volume andor Volume of Search'))

WebUI.setText(findTestObject('Object Repository/Extension/input_Extended Due Days_numberDays'), '6')

WebUI.verifyElementVisible(findTestObject('Object Repository/Extension/button_Save'))

WebUI.click(findTestObject('Object Repository/Extension/button_Save'))

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Object Repository/Extension/span_Request History Comments'))

WebUI.click(findTestObject('Page_foi.flow/comment/span_User Comments'))

WebUI.click(findTestObject('Object Repository/Extension/span_Request History Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), (((('Intake Flex has taken a 30 day Public Body extension. The new legislated due date is ' + 
    month) + ' ') + date1) + ' ') + year1)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Extension/svg_Pending_MuiSvgIcon-root'))

WebUI.click(findTestObject('Extension/li_Edit'))

//WebUI.setText(findTestObject('Object Repository/Extension/input_Extended Due Days_numberDays'), '')
WebUI.sendKeys(findTestObject('Object Repository/Extension/input_Extended Due Days_numberDays'), Keys.chord(Keys.BACK_SPACE))

WebUI.setText(findTestObject('Object Repository/Extension/input_Extended Due Days_numberDays'), '20')

WebUI.delay(4)

WebUI.click(findTestObject('Extension/span_Pending_MuiButtonBase-root MuiIconButton-root jss166 MuiRadio-root'))

//WebUI.click(findTestObject('Extension/button_Add Files (2)'))
//WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
//    '/Test Attachments/test2.docx')
def Format1 = 'yyyy-MM-dd'

def today = new Date()

def currentDate = today.format(Format1)

def approval = WebUI.getAttribute(findTestObject('Extension/input_Approved Date_approvedDate'), 'value').toString()

WebUI.verifyEqual(currentDate, approval)

WebUI.click(findTestObject('Object Repository/Extension/button_Save'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request details/Page_ABC-2099-7654195/input_Legislated Due Date_dueDate'), 
    0)

def ldds = WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/Page_ABC-2099-7654195/input_Legislated Due Date_dueDate'), 
    'value').toString()

println(ldds)

def mons = ldds.split('-')[1]

//prinln(mon)
def months = ''

if (mons == '01') {
    months = 'Jan'
}

if (mons == '02') {
    months = 'Feb'
}

if (mons == '03') {
    months = 'Mar'
}

if (mons == '04') {
    months = 'Apr'
}

if (mons == '05') {
    months = 'May'
}

if (mons == '06') {
    months = 'Jun'
}

if (mons == '07') {
    months = 'Jul'
}

if (mons == '08') {
    months = 'Aug'
}

if (mons == '09') {
    months = 'Sep'
}

//println(month)
def newldddate1s = Date.parse('yyyy-MM-dd', ldds).format('MM/dd/yyyy')

def newldddates = newldddate1s.toString()

def date1s = newldddates.split('/')[1]

def year1s = newldddates.split('/')[2]

WebUI.delay(3)

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Object Repository/Extension/span_Request History Comments'))

WebUI.click(findTestObject('Page_foi.flow/comment/span_User Comments'))

WebUI.click(findTestObject('Object Repository/Extension/span_Request History Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), (((('The OIPC has granted a 20 day extension. The new legislated due date is ' + 
    months) + ' ') + date1s) + ' ') + year1s)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'))

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Extension/svg_Approved_MuiSvgIcon-root'))

WebUI.click(findTestObject('Extension/li_Delete'))

WebUI.click(findTestObject('Extension/button_Continue'))

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.click(findTestObject('Object Repository/Extension/span_Request History Comments'))

WebUI.click(findTestObject('Page_foi.flow/comment/span_User Comments'))

WebUI.click(findTestObject('Object Repository/Extension/span_Request History Comments'))

WebUI.refresh()

WebUI.delay(5)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'Extension for OIPC - Large Volume and/or Volume of Search has been deleted.')

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            8), ('username') : findTestData('Login Credentials').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

//WebUI.click(findTestObject('Page_foi.flow/queue/div_Watching Requests'))
//WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))
//WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)
WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.refresh()

//WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))
WebUI.clickOffset(findTestObject('Page_foi.flow/navbar/notification/notification bell'), -2, 4)

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 request id'), requestID)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 message'), ((((('Extension taken for 30 days. The new legislated due date is ' + 
    month) + ' ') + date1) + ' ') + year1) + '.')

WebUI.clickOffset(findTestObject('Page_foi.flow/navbar/notification/notification bell'), -2, 4)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.closeBrowser()

