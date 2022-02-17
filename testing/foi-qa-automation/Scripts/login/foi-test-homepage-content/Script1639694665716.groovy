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

WebUI.delay(5, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/img'), 0)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/navbar/img'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/sign in/h1_Welcome, Sign In'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/sign in/h1_Welcome, Sign In'), 'Welcome, Sign In')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/sign in/button_Log In'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/sign in/button_Log In'), 'Log In')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/bottom menu/a_Help'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/bottom menu/a_Help'), 'Help')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/bottom menu/a_Contact'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/bottom menu/a_Contact'), 'Contact')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/bottom menu/a_Disclaimer'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/bottom menu/a_Disclaimer'), 'Disclaimer')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/bottom menu/a_Privacy'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/bottom menu/a_Privacy'), 'Privacy')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/bottom menu/a_Accessibility'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/bottom menu/a_Accessibility'), 'Accessibility')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/bottom menu/a_Copyright'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/bottom menu/a_Copyright'), 'Copyright')

