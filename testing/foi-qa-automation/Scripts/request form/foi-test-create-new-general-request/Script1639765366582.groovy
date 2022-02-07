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

WebUI.click(findTestObject('Page_foi.flow/li_assignee user option', [('user') : (lastname + ', ') + firstname]))

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Applicant First Name_MuiInputBase'), 'Firstname')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Applicant Last Name_MuiInputBase'), 'Lastname')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Applicant Email_MuiInputBase'), 'a@b.c')

WebUI.click(findTestObject('Page_foi.flow/form/inputs/div_Category'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_Individual'))

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Street Address_outlined-streetAddress'), '2210 Sooke Rd')

WebUI.setText(findTestObject('Object Repository/Page_foi.flow/input_Secondary Street Address_outlined-sco_3a97e9'), '1')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_City_outlined-city'), 'Victoria')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Province_outlined-province'), 'BC')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Country'), 'Canada')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Postal Code'), 'V9B0E3')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Home Phone_outlined-homePhone'), '6041234567')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/textarea_request description'), 'testing 123 description')

WebUI.click(findTestObject('Object Repository/Page_foi.flow/span_Description contains NO Personal Infor_c58cd5'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/span_EDU_checkmark'))

WebUI.scrollToElement(findTestObject('Object Repository/Page_foi.flow/span_EDU_checkmark'), 0)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Start Date'), 
    '002021-12-16')

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Received Date'), 
    '002021-12-16')

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/li_general'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Received Mode'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_Email'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Delivery Mode'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_Secure File Transfer'))

WebUI.scrollToElement(findTestObject('Object Repository/Page_foi.flow/button_Save'), 0)

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save'))

WebUI.delay(1)

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Return to Queue'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.maximizeWindow()

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 applicant name'), 'Lastname, Firstname')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 type'), 'General')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 state'), 'Intake In Progress')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 assignee'), 'Flex, Intake')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 received date'), '2021 Dec, 16')

