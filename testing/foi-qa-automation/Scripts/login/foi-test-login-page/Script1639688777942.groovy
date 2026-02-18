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

WebUI.click(findTestObject('Page_foi.flow/sign in/button_Log In'))

WebUI.click(findTestObject('Object Repository/Page_Log in to FOI/a_IDIR'))

WebUI.verifyElementVisible(findTestObject('Object Repository/Page_Government of British Columbia/a_B.C. government'))

WebUI.click(findTestObject('Object Repository/Page_Government of British Columbia/div_Log in with'))

WebUI.verifyElementPresent(findTestObject('Object Repository/Page_Government of British Columbia/div_Log in with'), 0)

WebUI.verifyElementPresent(findTestObject('Object Repository/Page_Government of British Columbia/div_Log in with'), 0)

WebUI.verifyElementText(findTestObject('Object Repository/Page_Government of British Columbia/div_Log in with'), 'Log in with')

WebUI.verifyElementPresent(findTestObject('Object Repository/Page_Government of British Columbia/span_Log in with_idirLogo'), 
    0)

WebUI.verifyElementText(findTestObject('Object Repository/Page_Government of British Columbia/span_Log in with_idirLogo'), 
    '')

WebUI.verifyElementPresent(findTestObject('Object Repository/Page_Government of British Columbia/label_IDIR Username'), 
    0)

WebUI.verifyElementText(findTestObject('Object Repository/Page_Government of British Columbia/label_IDIR Username'), 'IDIR Username')

WebUI.verifyElementPresent(findTestObject('Object Repository/Page_Government of British Columbia/input_IDIR Username_user'), 
    0)

WebUI.verifyElementVisible(findTestObject('Object Repository/Page_Government of British Columbia/label_Password'))

WebUI.verifyElementText(findTestObject('Object Repository/Page_Government of British Columbia/label_Password'), 'Password')

WebUI.verifyElementVisible(findTestObject('Object Repository/Page_Government of British Columbia/input_Password_password'))

WebUI.verifyElementVisible(findTestObject('Object Repository/Page_Government of British Columbia/input_Password_btnSubmit'))

WebUI.verifyElementText(findTestObject('Object Repository/Page_Government of British Columbia/input_Password_btnSubmit'), 
    '')

WebUI.verifyElementClickable(findTestObject('Object Repository/Page_Government of British Columbia/input_Password_btnSubmit'))

