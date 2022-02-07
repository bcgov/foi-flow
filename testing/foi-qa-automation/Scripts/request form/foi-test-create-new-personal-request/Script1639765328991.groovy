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

WebUI.click(findTestObject('Page_foi.flow/queue/button_Add Request'))

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned parent'), 'class').contains('Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Applicant First Name Parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Applicant Last Name Parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Applicant Email Parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Category Parent'), 'class').contains('Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Street Address parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_City parent'), 'class').contains('Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Province parent'), 'class').contains('Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Country parent'), 'class').contains('Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Postal Code parent'), 'class').contains('Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/textarea_request description parent'), 'class').contains('Mui-error') == 
true

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/span_Description contains NO Personal Infor_c58cd5'), 
        'color'), 'rgba(255, 0, 0, 1)', false)

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/h4_Select Ministry Client'), 'color'), 'rgba(255, 0, 0, 1)', 
    false)

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Request Type parent'), 'class').contains('Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Received Mode parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Delivery Mode parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Received Date parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Start Date parent'), 'class').contains('Mui-error') == true

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/li_assignee user option', [('user') : (lastname + ', ') + firstname]))

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/input_Applicant First Name_MuiInputBase'), 
    'required', 0)

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/input_Applicant Last Name_MuiInputBase'), 'required', 0)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Applicant First Name_MuiInputBase'), applicantFirstname)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Applicant Last Name_MuiInputBase'), applicantLastname)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Applicant Email_MuiInputBase'), email)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Category'))

WebUI.click(findTestObject(WebUI.concatenate(((['Object Repository/Page_foi.flow/li_', category]) as String[]))))

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Street Address_outlined-streetAddress'), streetAddress)

WebUI.setText(findTestObject('Object Repository/Page_foi.flow/input_Secondary Street Address_outlined-sco_3a97e9'), streetAddress2)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_City_outlined-city'), city)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Province_outlined-province'), province)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Country'), country)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Postal Code'), postalCode)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Home Phone_outlined-homePhone'), homePhone)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/textarea_request description'), description)

WebUI.click(findTestObject('Object Repository/Page_foi.flow/span_Description contains NO Personal Infor_c58cd5'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/span_EDU_checkmark'))

WebUI.scrollToElement(findTestObject('Object Repository/Page_foi.flow/span_EDU_checkmark'), 0)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Start Date'), startDateInput)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_Received Date'), receivedDateInput)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Request Type'))

WebUI.click(findTestObject(WebUI.concatenate(((['Object Repository/Page_foi.flow/li_', requestType]) as String[]))))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Received Mode'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Email'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Mail'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Fax'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Online Form'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/li_Online Form'), 'aria-disabled', 'true', 0)

WebUI.click(findTestObject(WebUI.concatenate(((['Object Repository/Page_foi.flow/li_', receivedMode]) as String[]))))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Delivery Mode'))

WebUI.click(findTestObject(WebUI.concatenate(((['Object Repository/Page_foi.flow/li_', deliveryMode]) as String[]))))

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned parent'), 'class').contains('Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Applicant First Name Parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Applicant Last Name Parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Applicant Email Parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Category Parent'), 'class').contains('Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Street Address parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_City parent'), 'class').contains('Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Province parent'), 'class').contains('Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Country parent'), 'class').contains('Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Postal Code parent'), 'class').contains('Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/textarea_request description parent'), 'class').equals('Mui-error') == 
false

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/span_Description contains NO Personal Infor_c58cd5'), 
        'color'), 'rgba(0, 0, 0, 0.87)', false)

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/h4_Select Ministry Client'), 'color'), 'rgba(0, 0, 0, 0.87)', 
    false)

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Request Type parent'), 'class').contains('Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Received Mode parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Delivery Mode parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Received Date parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_Start Date parent'), 'class').contains('Mui-error') == false

WebUI.scrollToElement(findTestObject('Object Repository/Page_foi.flow/button_Save'), 0)

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save'))

WebUI.delay(1)

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Return to Queue'))

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.maximizeWindow()

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 applicant name'), 'Lastname, Firstname')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 type'), 'Personal')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 state'), 'Intake In Progress')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 assignee'), WebUI.concatenate((([lastname, ', '
                , firstname]) as String[])))

WebUI.callTestCase(findTestCase('request form/foi-test-request-fields-populated'), [('firstname') : 'Intake', ('lastname') : 'Flex', ('applicantFirstname') : applicantFirstname
        , ('applicantLastname') : applicantLastname, ('email') : email, ('category') : category, ('streetAddress') : streetAddress
        , ('streetAddress2') : streetAddress2, ('city') : city, ('province') : province, ('country') : country, ('postalCode') : postalCode
        , ('homePhone') : homePhone, ('description') : description, ('startDate') : startDate, ('receivedDate') : receivedDate
        , ('requestType') : requestType, ('receivedMode') : receivedMode, ('deliveryMode') : deliveryMode], FailureHandling.STOP_ON_FAILURE)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    WebUI.openBrowser(GlobalVariable.BASE_URL)

    WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)
}

