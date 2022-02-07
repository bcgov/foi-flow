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

WebUI.maximizeWindow()

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Applicant First Name_MuiInputBase'), 
    'value', applicantFirstname, 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Applicant Last Name_MuiInputBase'), 
    'value', applicantLastname, 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Applicant Email_MuiInputBase'), 
    'value', email, 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/inputs/div_Category'), category)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Street Address_outlined-streetAddress'), 
    'value', streetAddress, 0)

WebUI.verifyElementAttributeValue(findTestObject('Object Repository/Page_foi.flow/input_Secondary Street Address_outlined-sco_3a97e9'), 
    'value', streetAddress2, 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_City_outlined-city'), 'value', city, 
    0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Province_outlined-province'), 'value', 
    province, 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Country'), 'value', 
    country, 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Postal Code'), 
    'value', postalCode, 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Home Phone_outlined-homePhone'), 
    'value', homePhone, 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/textarea_request description'), 'value', description, 0)

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/input_noPICheckbox'), 'checked', 0)

WebUI.verifyElementHasAttribute(findTestObject('Page_foi.flow/form/inputs/input_EDU checkbox'), 'checked', 0)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/input_Request Type'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Start Date'), 
    'value', startDate, 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/input_Received Date'), 
    'value', receivedDate, 0)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    WebUI.openBrowser(GlobalVariable.BASE_URL)

    WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)
}

