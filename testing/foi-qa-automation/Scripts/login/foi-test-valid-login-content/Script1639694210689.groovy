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

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('username') : username, ('password') : password], FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/span_username'), (firstname + ' ') + lastname)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/navbar/span_username'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/navbar/img'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/queue/h3_Your FOI Request Queue'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/h3_Your FOI Request Queue'), 'Your FOI Request Queue')

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/queue/h3_Your FOI Request Queue'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/queue/h3_Advanced Search'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/h3_Advanced Search'), 'Advanced Search')

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/queue/h3_Advanced Search'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_Watching Requests'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_My Requests'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_My Team Requests'), 0)

assert WebUI.getAttribute(findTestObject('Page_foi.flow/queue/div_My Requests'), 'class').contains('MuiChip-filledPrimary')

assert WebUI.getAttribute(findTestObject('Page_foi.flow/queue/div_Watching Requests'), 'class').contains('MuiChip-outlinedPrimary')

assert WebUI.getAttribute(findTestObject('Page_foi.flow/queue/div_My Team Requests'), 'class').contains('MuiChip-outlinedPrimary')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), 0)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/queue/button_Add Request'))

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/queue/button_Add Request'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/navbar/notification/notification bell'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/navbar/reporting link'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/button_Sign Out'), 'Sign Out')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/queue/nav_pagination'))

WebUI.click(findTestObject('Page_foi.flow/navbar/Page_ABC-2099-50/svg_FOI Intake_bi bi-bar-chart-line'), FailureHandling.STOP_ON_FAILURE)

WebUI.switchToWindowIndex(1, FailureHandling.STOP_ON_FAILURE)

assert WebUI.getUrl() == 'https://dev.reports.foirequests.gov.bc.ca/'

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/queue/h3_Your FOI Request Queue'))

