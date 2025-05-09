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

WebUI.maximizeWindow(FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/h3_Advanced Search'))

WebUI.click(findTestObject('Page_foi.flow/queue/advanced search/div_advanced search field selector ID NUMBER'))

WebUI.setText(findTestObject('Page_foi.flow/queue/advanced search/input_advancedSearch'), requestID)

WebUI.click(findTestObject('Page_foi.flow/queue/Page_FOI Advanced Search/div_All'))

WebUI.click(findTestObject('Page_foi.flow/queue/Page_FOI Advanced Search/Page_FOI Advanced Search/span_Unopened'))

WebUI.click(findTestObject('Page_FOI Advanced Search/div_Clear All Filters_MuiBackdrop-root MuiBackdrop-invisible MuiModal-backdrop css-esi9ax'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/queue/advanced search/button_Apply Search'), 0)

WebUI.click(findTestObject('Page_foi.flow/queue/advanced search/button_Apply Search'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.scrollToElement(findTestObject('Page_FOI Advanced Search/div_general'), 0)

WebUI.click(findTestObject('Page_FOI Advanced Search/Page_FOI Advanced Search/div_general'))

