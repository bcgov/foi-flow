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

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/button_Add Request'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + 
            firstname]))

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant First Name_MuiInputBase'), 'Firstname')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Last Name_MuiInputBase'), 'Lastname')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Email_MuiInputBase'), 'a@b.c')

WebUI.click(findTestObject('Page_foi.flow/form/inputs/applicant details/div_Category'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Individual'))

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Street Address_outlined-streetAddress'), '2210 Sooke Rd')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Secondary Street Address'), '1')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_City_outlined-city'), 'Victoria')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Province_outlined-province'), 'BC')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Country'), 'Canada')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Postal Code'), 'V9B0E3')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Home Phone_outlined-homePhone'), '6041234567')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description'), 'testing 123 description')

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_EDU_checkmark'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request description/span_EDU_checkmark'), 0)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request details/input_Start Date'), '002021-12-16')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date'), '002021-12-16')

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/request type options/li_general'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description'), 0)

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'), 
        'color'), 'rgba(255, 0, 0, 1)', false)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'))

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'), 
        'color'), 'rgba(0, 0, 0, 0.87)', false)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Mode'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/received mode options/li_Email'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Delivery Mode'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/delivery mode options/li_Secure File Transfer'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

def requestID = WebUI.getUrl(FailureHandling.STOP_ON_FAILURE).split('/')[5]

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.maximizeWindow()

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 applicant name'), 'Lastname, Firstname')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 type'), 'General')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 state'), 'Intake In Progress')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 assignee'), 'Flex, Intake')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 received date'), 'DEC 16 2021')

