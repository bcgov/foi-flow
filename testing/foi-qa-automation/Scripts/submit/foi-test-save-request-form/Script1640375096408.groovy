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
import groovy.json.JsonSlurper as JsonSlurper

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : password, ('username') : username], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_Intake, FOI (1)'))

//WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + 
//           firstname]))
WebUI.setText(findTestObject('Page_foi.flow/form/inputs/input_AXIS ID Number'), 'EDU-2099-' + requestID)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/applicant details/div_Category'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/form/inputs/applicant details/category dropdown/li_' + findTestData(
            'Sample Applicant').getValue('category', 1)))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request description/textarea_request description'), 0)

if (WebUI.getText(findTestObject('Page_foi.flow/form/inputs/request details/input_Request Type'), FailureHandling.STOP_ON_FAILURE) == 
'general') {
    WebUI.click(findTestObject('Page_foi.flow/form/inputs/request description/span_no PI Checkbox'))
}

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request details/input_Delivery Mode'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/input_Delivery Mode'))

WebUI.click(findTestObject('Page_foi.flow/form/inputs/request details/delivery mode options/li_Secure File Transfer'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/div_The request has been saved successfully'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'))

//WebUI.verifyElementPresent(findTestObject('Page_foi.flow/div_The request has been saved successfully'), 0)
WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

return requestID

@com.kms.katalon.core.annotation.SetUp
def setup() {
    if (sendRequest) {
        def response = WS.sendRequest(findTestObject('FoiRawRequest'))

        def jsonSlurper = new JsonSlurper()

        requestID = jsonSlurper.parseText(response.responseText).id.toString()

        WS.verifyResponseStatusCode(response, 200)
    }
}

