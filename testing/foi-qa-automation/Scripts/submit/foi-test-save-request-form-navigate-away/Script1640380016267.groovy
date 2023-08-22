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
import org.openqa.selenium.remote.server.handler.GetAlertText as GetAlertText
import org.openqa.selenium.remote.server.handler.GetAlertText as Keys
import groovy.json.JsonSlurper as JsonSlurper

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Return to Queue'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyMatch(WebUI.getUrl(), GlobalVariable.BASE_URL + '/foi/dashboard', false)

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/address/svg_Category_MuiSvgIcon-root'), 0)

WebUI.waitForElementClickable(findTestObject('Page_foi.flow/form/inputs/address/svg_Category_MuiSvgIcon-root'), 0)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/applicant details/input_Applicant Last Name Parent'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/address/svg_Category_MuiSvgIcon-root'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/address/div_ADDRESS AND CONTACT INFORMATION header'), FailureHandling.STOP_ON_FAILURE)

WebUI.setText(findTestObject('Page_foi.flow/form/inputs/address/input_Street Address_outlined-streetAddress'), streetAddress)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Return to Queue'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyAlertPresent(0)

//WebUI.verifyMatch(WebUI.getAlertText(), 'Are you sure you want to leave? Your changes will be lost.', false)
WebUI.dismissAlert(FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/inputs/address/input_Street Address_outlined-streetAddress'), 
    'value', streetAddress, 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Return to Queue'), FailureHandling.STOP_ON_FAILURE)

WebUI.acceptAlert(FailureHandling.STOP_ON_FAILURE)

WebUI.verifyMatch(WebUI.getUrl(), GlobalVariable.BASE_URL + '/foi/dashboard', false)

WebUI.closeBrowser()

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

