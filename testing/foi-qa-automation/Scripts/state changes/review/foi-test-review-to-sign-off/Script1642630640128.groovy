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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : findTestData('New Test Data').getValue('Password', 
            2), ('username') : findTestData('New Test Data').getValue('Username', 2), ('firstname') : findTestData('New Test Data').getValue(
            'First Name', 2), ('lastname') : findTestData('New Test Data').getValue('Last Name', 2), ('applicantFirstname') : ''
        , ('applicantLastname') : '', ('category') : '', ('email') : findTestData('Sample Applicant').getValue('email', 
            1), ('streetAddress') : findTestData('Sample Applicant').getValue('streetAddress', 1), ('streetAddress2') : findTestData(
            'Sample Applicant').getValue('streetAddress2', 1), ('city') : findTestData('Sample Applicant').getValue('city', 
            1), ('province') : findTestData('Sample Applicant').getValue('province', 1), ('country') : findTestData('Sample Applicant').getValue(
            'country', 1), ('postalCode') : findTestData('Sample Applicant').getValue('postalCode', 1), ('homePhone') : findTestData(
            'Sample Applicant').getValue('homePhone', 1), ('description') : findTestData('Sample Applicant').getValue('description', 
            1), ('startDate') : '', ('receivedDate') : '', ('receivedMode') : '', ('requestType') : '', ('deliveryMode') : ''], 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_Open'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/li_Call For Records'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebDriver IAOuser = DriverFactory.getWebDriver()

WebDriver ministryUser = CustomKeywords.'browser.newWindow.open'()

DriverFactory.changeWebDriver(ministryUser)

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('New Test Data').getValue('Password', 8)
        , ('username') : findTestData('New Test Data').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/div_ministry assigned to'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/li_ministry assignee foiedu, foiedu'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division dropdown'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_Education Programs'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division stage'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/dropdown options/li_Assigned to Division'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/li_Records Review'))

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + '/Test Attachments/test.docx')

WebUI.click(findTestObject('Object Repository/Page_foi.flow/button_Save Change'))

WebUI.delay(1, FailureHandling.STOP_ON_FAILURE)

DriverFactory.changeWebDriver(IAOuser)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Ministry Sign Off'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Call For Records'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Closed'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Consult'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/li_Response'), 0)

WebUI.click(findTestObject('Page_foi.flow/li_Ministry Sign Off'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/div_State Change Dialog'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/td_Next Assignee'), 'Processing Team')

WebUI.verifyElementText(findTestObject('Page_foi.flow/span_State Change Dialog message'), ('Are you sure you want to change Request #' + 
    WebUI.getText(findTestObject('Page_foi.flow/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)) + ' to Ministry Sign Off?')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/button_Save Change'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/button_Cancel'), 0)

WebUI.click(findTestObject('Page_foi.flow/button_Cancel'))

WebUI.delay(1, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Records Review', 0)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 state'), 'Records Review')

DriverFactory.changeWebDriver(ministryUser)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 state'), 'Records Review')

DriverFactory.changeWebDriver(IAOuser)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'))

WebUI.click(findTestObject('Page_foi.flow/li_Ministry Sign Off'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/div_State Change Dialog'), 0)

WebUI.click(findTestObject('Page_foi.flow/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(1, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/sidebar/status dropdown/input_Status'), 'value', 'Ministry Sign Off', 0)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 state'), 'Ministry Sign Off')

DriverFactory.changeWebDriver(ministryUser)

WebUI.navigateToUrl(GlobalVariable.BASE_URL + '/foi/dashboard')

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/div_request queue row 1 state'), 'Ministry Sign Off')

