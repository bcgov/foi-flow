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
        , ('category') : '', ('email') : findTestData('Sample Applicant').getValue('email', 1), ('streetAddress') : findTestData(
            'Sample Applicant').getValue('streetAddress', 1), ('streetAddress2') : findTestData('Sample Applicant').getValue(
            'streetAddress2', 1), ('city') : findTestData('Sample Applicant').getValue('city', 1), ('province') : findTestData(
            'Sample Applicant').getValue('province', 1), ('country') : findTestData('Sample Applicant').getValue('country', 
            1), ('postalCode') : findTestData('Sample Applicant').getValue('postalCode', 1), ('homePhone') : findTestData(
            'Sample Applicant').getValue('homePhone', 1), ('description') : findTestData('Sample Applicant').getValue('description', 
            1), ('startDate') : '', ('receivedDate') : '', ('receivedMode') : '', ('requestType') : '', ('deliveryMode') : ''], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Redirect'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Closed'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Redirect'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/div_State Change Dialog'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Redirect', 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments (2)')

//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1'), 0)

//WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), ((firstname + ' ') + lastname) + 
    //' changed the state of the request to Redirect')
