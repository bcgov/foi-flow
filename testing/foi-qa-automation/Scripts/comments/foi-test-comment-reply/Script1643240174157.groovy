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

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'test comment')

WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_comment Reply_form'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_comment list 1 Reply button'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_comment Reply_form'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Reply_cancelBtn'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_comment Reply_form'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_comment list 1 Reply button'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_comment reply text area'), 'test reply')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/button_reply 1 Reply'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_comment reply 1'), 0)

//def today = new Date()
WebUI.click(findTestObject('Page_foi.flow/comment/button_reply 1_postBtn'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_comment reply 1 date'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_comment reply 1 user'), (lastname + ', ') + firstname)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment reply 1 text'), 'test reply')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_comment reply 1'), 0)

WebUI.verifyElementNotVisible(findTestObject('Page_foi.flow/comment/button_comment list 1 Reply button'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/button_reply 1 Reply'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_reply 1 Reply'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_comment reply 2 text area'), 'test reply 2')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/button_reply 2 Reply'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_comment reply 2'), 0)

//today = new Date()
WebUI.click(findTestObject('Page_foi.flow/comment/button_reply 2_postBtn'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_comment reply 2 date'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_comment reply 2 user'), (lastname + ', ') + firstname)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment reply 2 text'), 'test reply 2')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_comment reply 2'), 0)

WebUI.verifyElementNotVisible(findTestObject('Page_foi.flow/comment/button_reply 1 Reply'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/button_reply 2 Reply'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_reply 2 Reply'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_comment reply 3 text area'), 'test reply 3')

WebUI.click(findTestObject('Page_foi.flow/comment/button_reply 3_postBtn'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_reply 3 Reply'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_comment reply 4 text area'), 'test reply 4')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/span_Show more comment replies'), 0)

WebUI.scrollToElement(findTestObject('Page_foi.flow/comment/button_reply 4_postBtn'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_reply 4_postBtn'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/span_Show more comment replies'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/span_Show more comment replies'), 'Show more comments')

WebUI.verifyElementNotVisible(findTestObject('Page_foi.flow/comment/div_comment reply 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotVisible(findTestObject('Page_foi.flow/comment/div_comment reply 2'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/comment/div_comment reply 3'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/comment/div_comment reply 4'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/span_Show more comment replies'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/span_Show more comment replies'), 'Show fewer comments')

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/comment/div_comment reply 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/comment/div_comment reply 2'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/comment/div_comment reply 3'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/comment/div_comment reply 4'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/span_Show more comment replies'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotVisible(findTestObject('Page_foi.flow/comment/div_comment reply 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotVisible(findTestObject('Page_foi.flow/comment/div_comment reply 2'), FailureHandling.STOP_ON_FAILURE)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

