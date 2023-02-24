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

WebUI.maximizeWindow(FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/button_Add Request'))

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_AXIS ID Number Parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned parent'), 'class').contains(
    'Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant First Name Parent'), 
    'class').contains('Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Last Name Parent'), 
    'class').contains('Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Email Parent'), 'class').contains(
    'Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Category Parent'), 'class').contains(
    'Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/address/input_Street Address parent'), 'class').contains(
    'Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/address/input_City parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/address/input_Province parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/address/input_Country parent'), 'class').contains('Mui-error') == 
true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/address/input_Postal Code parent'), 'class').contains(
    'Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description parent'), 
    'class').contains('Mui-error') == true

//WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/form/h4_Select Ministry Client'), 'color'), 'rgba(255, 0, 0, 1)', 
//    false)
assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type parent'), 'class').contains(
    'Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Mode parent'), 'class').contains(
    'Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Delivery Mode parent'), 'class').contains(
    'Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date parent'), 'class').contains(
    'Mui-error') == true

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Start Date parent'), 'class').contains(
    'Mui-error') == true

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + 
            firstname]))

Random random = new Random()

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_AXIS ID Number'), 'ABC-2099-' + random.nextInt(10000000 //generate random axis number for sake of test
        ))

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant First Name_MuiInputBase'), 
    'required', 0)

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Last Name_MuiInputBase'), 
    'required', 0)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant First Name_MuiInputBase'), applicantFirstname)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Last Name_MuiInputBase'), applicantLastname)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Email_MuiInputBase'), email)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Category'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/applicant details/category dropdown/li_Individual'), FailureHandling.STOP_ON_FAILURE)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Street Address_outlined-streetAddress'), streetAddress)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Secondary Street Address'), streetAddress2)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_City_outlined-city'), city)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Province_outlined-province'), province)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Country'), country)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Postal Code'), postalCode)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Home Phone_outlined-homePhone'), homePhone)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description'), description)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_EDU_selectspanEDU'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request details/input_Start Date'), '2021-12-16')

WebUI.waitForElementClickable(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date_receivedDate'), 
    0)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date_receivedDate'), '2021-12-16')

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date_receivedDate'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/request type options/li_personal'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Mode'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/request details/received mode options/li_Email'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/request details/received mode options/li_Mail'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/request details/received mode options/li_Fax'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/inputs/request details/received mode options/li_Online Form'), 
    0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/request details/received mode options/li_Online Form'), 
    'aria-disabled', 'true', 0)

WebUI.click(findTestObject(WebUI.concatenate(((['Object Repository/Page_foi.flow/form/inputs/request details/received mode options/li_'
                    , receivedMode]) as String[]))))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Delivery Mode'))

WebUI.click(findTestObject(WebUI.concatenate(((['Object Repository/Page_foi.flow/form/inputs/request details/delivery mode options/li_'
                    , deliveryMode]) as String[]))))

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned parent'), 'class').contains(
    'Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/input_AXIS ID Number Parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant First Name Parent'), 
    'class').contains('Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Last Name Parent'), 
    'class').contains('Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Email Parent'), 'class').contains(
    'Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Category Parent'), 'class').contains(
    'Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/address/input_Street Address parent'), 'class').contains(
    'Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/address/input_City parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/address/input_Province parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/address/input_Country parent'), 'class').contains('Mui-error') == 
false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/address/input_Postal Code parent'), 'class').contains(
    'Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description parent'), 
    'class').equals('Mui-error') == false

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/form/h4_Select Ministry Client'), 'color'), 'rgba(0, 0, 0, 0.87)', 
    false)

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type parent'), 'class').contains(
    'Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Mode parent'), 'class').contains(
    'Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Delivery Mode parent'), 'class').contains(
    'Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Received Date parent'), 'class').contains(
    'Mui-error') == false

assert WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/input_Start Date parent'), 'class').contains(
    'Mui-error') == false

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

def requestID = WebUI.getUrl(FailureHandling.STOP_ON_FAILURE).split('/')[5 // put back in after axis is phased out
]

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.maximizeWindow()

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 applicant name'), 'Lastname, Firstname')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 type'), 'Personal')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 state'), 'Intake In Progress')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 assignee'), WebUI.concatenate((([lastname
                , ', ', firstname]) as String[])))

WebUI.callTestCase(findTestCase('form/foi-test-request-fields-populated'), [('firstname') : 'Intake', ('lastname') : 'Flex'
        , ('applicantFirstname') : applicantFirstname, ('applicantLastname') : applicantLastname, ('email') : email, ('category') : category
        , ('streetAddress') : streetAddress, ('streetAddress2') : streetAddress2, ('city') : city, ('province') : province
        , ('country') : country, ('postalCode') : postalCode, ('homePhone') : homePhone, ('description') : description, ('startDate') : startDate
        , ('receivedDate') : receivedDate, ('requestType') : requestType, ('receivedMode') : receivedMode, ('deliveryMode') : deliveryMode], 
    FailureHandling.STOP_ON_FAILURE)

