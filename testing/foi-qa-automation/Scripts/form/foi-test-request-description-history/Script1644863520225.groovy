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
        , ('category') : '', ('email') : findTestData('Sample Applicant').getValue('email', 1), ('streetAddress') : findTestData('Sample Applicant').getValue('streetAddress', 1)
        , ('streetAddress2') : findTestData('Sample Applicant').getValue('streetAddress2', 1), ('city') : findTestData('Sample Applicant').getValue('city', 1)
        , ('province') : findTestData('Sample Applicant').getValue('province', 1), ('country') : findTestData('Sample Applicant').getValue('country', 1)
        , ('postalCode') : findTestData('Sample Applicant').getValue('postalCode', 1), ('homePhone') : findTestData('Sample Applicant').getValue('homePhone', 1)
        , ('description') : findTestData('Sample Applicant').getValue('description', 1), ('startDate') : '', ('receivedDate') : ''
        , ('receivedMode') : '', ('requestType') : '', ('deliveryMode') : ''], FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/request description/input_noPICheckbox'), 'disabled', 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Intake in Progress', 0)

WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/form/description history/button_Description History'))

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description'), 'test analyst update')

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/form/description history/button_Description History'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/address/input_Country'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/description history/button_Description History') 
    )

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/description history/p_request description history entry 1'), description)