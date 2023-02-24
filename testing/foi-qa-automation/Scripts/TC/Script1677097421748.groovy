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

WebUI.openBrowser('')

WebUI.navigateToUrl('http://foiflow.local:3000/')

WebUI.click(findTestObject('Page_foi.flow/button_Log In'))

WebUI.setText(findTestObject('Page_Sign in to foi-mod/input_Username_username'), 'foiintake@idir')

WebUI.setEncryptedText(findTestObject('Page_Sign in to foi-mod/input_Password_password'), '4fqcoPhx3Nk=')

WebUI.sendKeys(findTestObject('Page_Sign in to foi-mod/input_Password_password'), Keys.chord(Keys.ENTER))

WebUI.click(findTestObject('Page_FOI Request Queue/div_Intake in Progress'))

WebUI.click(findTestObject('Page_ABC-2099-5350075/button_Watch'))

WebUI.click(findTestObject('Object Repository/Page_foi.flow/form/watch/button_Unwatch'))

WebUI.setText(findTestObject('Page_ABC-2099-5350075/input_Applicant First Name_firstName'), 'Firstnamezxc')

WebUI.click(findTestObject('Page_ABC-2099-5350075/span_TRA_selectspanTRA'))

WebUI.click(findTestObject('Page_ABC-2099-5350075/span_TRA_selectspanTRA'))

WebUI.click(findTestObject('Page_ABC-2099-5350075/body_FOI  FOI Intake 17Sign OutABC-2099-535_4f9c95'))

WebUI.click(findTestObject('Page_ABC-2099-5350075/li_Mail'))

WebUI.click(findTestObject('Page_ABC-2099-5350075/button_Save'))

