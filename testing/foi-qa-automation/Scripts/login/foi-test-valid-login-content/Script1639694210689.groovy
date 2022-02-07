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

WebUI.click(findTestObject('Object Repository/Page_foi.flow/span_Intake User'))

WebUI.verifyElementText(findTestObject('Object Repository/Page_foi.flow/span_Intake User'), WebUI.concatenate((([firstname
                , ' ', lastname]) as String[])))

WebUI.verifyElementVisible(findTestObject('Object Repository/Page_foi.flow/span_Intake User'))

WebUI.verifyElementVisible(findTestObject('Object Repository/Page_foi.flow/img'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/queue/h3_Your FOI Request Queue'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/queue/h3_Your FOI Request Queue'), 'Your FOI Request Queue')

WebUI.verifyElementVisible(findTestObject('Object Repository/Page_foi.flow/div_My Requests Watching Requests My Team Requests'))

WebUI.verifyElementText(findTestObject('Object Repository/Page_foi.flow/div_My Requests Watching Requests My Team Requests'), 
    'My Requests Watching Requests My Team Requests')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/input_Watching Requests'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/input_My Requests'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/input_My Team Requests'))

WebUI.verifyElementClickable(findTestObject('Object Repository/Page_foi.flow/input_Add Request_form-control'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/queue/div_Your FOI Request QueueAdd Request'))

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/notification bell'))

WebUI.verifyElementVisible(findTestObject('Object Repository/Page_foi.flow/button_Sign Out'))

WebUI.verifyElementText(findTestObject('Object Repository/Page_foi.flow/button_Sign Out'), 'Sign Out')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/queue/pagination counter'))

WebUI.verifyElementVisible(findTestObject('Object Repository/Page_foi.flow/div_No_MuiTablePagination-actions'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header APPLICANT NAME'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header REQUEST TYPE'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header ID NUMBER'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header CURRENT STATE'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header ASSIGNED TO'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header RECEIVED DATE'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_queue header XGOV'), 0)

