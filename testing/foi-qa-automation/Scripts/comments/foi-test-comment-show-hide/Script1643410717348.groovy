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
import groovy.json.JsonSlurper as JsonSlurper

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'test comment')

WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'test comment')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment list 1 user'), (lastname + ', ') + firstname)

WebUI.click(findTestObject('Page_foi.flow/comment/Page_ABC-2099-50/span_Request History Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), ((firstname + ' ') + lastname) + 
    ' changed the state of the request to Open')

WebUI.click(findTestObject('Page_foi.flow/comment/Page_ABC-2099-50/span_User Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'test comment')

WebUI.click(findTestObject('Page_foi.flow/comment/Page_ABC-2099-50/span_All'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'test comment')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment list 1 user'), (lastname + ', ') + firstname)

for (int i = 2; i < 10; i++) {
    WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

    WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'test comment ' + i)

    WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)
}

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/comment/button_Show more comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'test comment 10')

WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotVisible(findTestObject('Page_foi.flow/comment/div_Comment list 11'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/comment/button_Show more comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/comment/button_Show more comments'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Show more comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/comment/div_Comment list 11'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotVisible(findTestObject('Page_foi.flow/comment/button_Show more comments'), FailureHandling.STOP_ON_FAILURE)

