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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : findTestData('New Test Data').getValue('Password', 
            6), ('username') : findTestData('New Test Data').getValue('Username', 6), ('firstname') : findTestData('New Test Data').getValue(
            'First Name', 6), ('lastname') : findTestData('New Test Data').getValue('Last Name', 6), ('applicantFirstname') : ''
        , ('applicantLastname') : '', ('category') : '', ('email') : findTestData('Sample Applicant').getValue('email', 
            1), ('streetAddress') : findTestData('Sample Applicant').getValue('streetAddress', 1), ('streetAddress2') : findTestData(
            'Sample Applicant').getValue('streetAddress2', 1), ('city') : findTestData('Sample Applicant').getValue('city', 
            1), ('province') : findTestData('Sample Applicant').getValue('province', 1), ('country') : findTestData('Sample Applicant').getValue(
            'country', 1), ('postalCode') : findTestData('Sample Applicant').getValue('postalCode', 1), ('homePhone') : findTestData(
            'Sample Applicant').getValue('homePhone', 1), ('description') : findTestData('Sample Applicant').getValue('description', 
            1), ('startDate') : '', ('receivedDate') : '', ('receivedMode') : '', ('requestType') : '', ('deliveryMode') : ''], 
    FailureHandling.STOP_ON_FAILURE)

'\r\n'
WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/input_Request Type'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Request Type'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_general'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_Open'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/div_State Change Dialog'), 0)

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Open', 0)

WebUI.refresh(FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/div_add other watchers'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/li_Processing Team'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Flex Team'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_close dropdown'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Flex Team'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/li_Processing Team'), 0)

WebUI.click(findTestObject('Page_foi.flow/li_assignee user option', [('user') : (lastname + ', ') + firstname]))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/li_Flex Team'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/input_Request Type'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/li_personal'))

WebUI.scrollToElement(findTestObject('Object Repository/Page_foi.flow/button_Save'), 0)

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save'))

WebUI.delay(1, FailureHandling.STOP_ON_FAILURE)

WebUI.waitForElementPresent(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/li_Flex Team'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Processing Team'), 0)

WebUI.click(findTestObject('Page_foi.flow/li_Processing Team'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/div_add other watchers'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Processing Team'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/li_Flex Team'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_close dropdown'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/input_EDU checkbox'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Request Type'))

WebUI.click(findTestObject('Page_foi.flow/li_general'))

WebUI.scrollToElement(findTestObject('Object Repository/Page_foi.flow/button_Save'), 0)

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save'))

WebUI.delay(1, FailureHandling.STOP_ON_FAILURE)

WebUI.waitForElementPresent(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Flex Team'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/li_Processing Team'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_close dropdown'))

WebUI.click(findTestObject('Page_foi.flow/div_add other watchers'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/li_Processing Team'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Flex Team'), 0)

