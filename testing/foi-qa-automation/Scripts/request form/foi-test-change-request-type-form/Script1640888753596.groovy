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

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1 applicant name'))

'\r\n'
WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/input_Request Type'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Request Type'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_general'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/input_Applicant Email_MuiInputBase'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/div_CHILD DETAILSFirst NameFirst NameMiddle_3eab06'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/div_ON BEHALF OF DETAILSFirst NameFirst Nam_13a6b9'), 0)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/input_Request Type'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/inputs/input_Request Type'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/li_personal'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/div_CHILD DETAILSFirst NameFirst NameMiddle_3eab06'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/div_CHILD DETAILSFirst NameFirst NameMiddle_3eab06'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/label_CHILD DETAILS'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/div_ON BEHALF OF DETAILSFirst NameFirst Nam_13a6b9'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/label_ON BEHALF OF DETAILS'), 0)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    WS.verifyResponseStatusCode(response, 200)

    WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)
}

