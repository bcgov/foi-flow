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
import groovy.json.JsonSlurper as JsonSlurper

WebUI.openBrowser('')

WebUI.navigateToUrl('https://dev.foirequests.gov.bc.ca/')

WebUI.click(findTestObject('Object Repository/Inputamount_trial/Page_foi.flow/button_Log In'))

WebUI.setText(findTestObject('Object Repository/Inputamount_trial/Page_Sign in to foi-mod/input_Username_username'), 'foiintakeflex@idir')

WebUI.setEncryptedText(findTestObject('Object Repository/Inputamount_trial/Page_Sign in to foi-mod/input_Password_password'), 
    '4fqcoPhx3Nk=')

WebUI.sendKeys(findTestObject('Object Repository/Inputamount_trial/Page_Sign in to foi-mod/input_Password_password'), Keys.chord(
        Keys.ENTER))

WebUI.click(findTestObject('Page_foi.flow/queue/div_Watching Requests'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), 'ABC-2099-14138')

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('CFR/div_CFR Form'))

//WebUI.sendKeys(findTestObject(‘CFR/input_Amount Paid_amountPaid'), Keys.chord(Keys.CONTROL, ‘a’))
//WebUI.sendKeys(findTestObject(‘CFR/input_Amount Paid_amountPaid’), Keys.chord(Keys.BACK_SPACE))
WebUI.doubleClick(findTestObject('CFR/input_Amount Paid_amountPaid'))

WebUI.sendKeys(findTestObject('CFR/input_Amount Paid_amountPaid'), Keys.chord(Keys.BACK_SPACE))

WebUI.sendKeys(findTestObject('CFR/input_Amount Paid_amountPaid'), Keys.chord(Keys.BACK_SPACE))

WebUI.sendKeys(findTestObject('CFR/input_Amount Paid_amountPaid'), Keys.chord(Keys.BACK_SPACE))

WebUI.sendKeys(findTestObject('CFR/input_Amount Paid_amountPaid'), Keys.chord(Keys.BACK_SPACE))

WebUI.sendKeys(findTestObject('CFR/input_Amount Paid_amountPaid'), Keys.chord(Keys.BACK_SPACE))

WebUI.sendKeys(findTestObject('CFR/input_Amount Paid_amountPaid'), Keys.chord(Keys.BACK_SPACE))

WebUI.sendKeys(findTestObject('CFR/input_Amount Paid_amountPaid'), Keys.chord(Keys.BACK_SPACE))

WebUI.delay(4)

WebUI.sendKeys(findTestObject('CFR/input_Amount Paid_amountPaid'), '380')

//WebUI.setText(findTestObject('CFR/input_Amount Paid_amountPaid'), '0')
WebUI.setText(findTestObject('CFR/input_Amount Paid_amountPaid'), '380')

WebUI.setText(findTestObject('CFR/input_Fee Waiver Amount_feewaiverAmount'), '50')

WebUI.click(findTestObject('CFR/div_270.8'))

println(WebUI.getAttribute(findTestObject('CFR/input_Balance Remaining_balanceRemaining'), 'value').toString())

def _val = WebUI.getAttribute(findTestObject('CFR/input_Balance Remaining_balanceRemaining'), 'value').toString()

WebUI.verifyEqual(_val, '50.00')

WebUI.click(findTestObject('CFR/Payment_Info/div_Select Payment Method'))

WebUI.click(findTestObject('CFR/Payment_Info/li_Credit Card - Phone'))

WebUI.scrollToElement(findTestObject('CFR/button_Save'), 0)

