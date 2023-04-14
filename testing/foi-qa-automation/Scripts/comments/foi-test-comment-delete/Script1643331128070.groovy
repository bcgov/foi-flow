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

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'test comment')

WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'test comment 2')

WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'test comment 3')

WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 2 text'), 'test comment 2')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'test comment 3')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 3'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Comment 2 Reply_actionsBtn'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Delete Comment  modal'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_comment Delete'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Delete Comment  modal'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Delete comment modal Cancel'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 2 text'), 'test comment 2')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'test comment 3')

WebUI.click(findTestObject('Page_foi.flow/comment/button_Comment 2 Reply_actionsBtn'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_comment Delete'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Delete comment modal confirm'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 2 text'), 'test comment')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'test comment 3')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment list 3'), 0)

WebDriver user1 = DriverFactory.getWebDriver()

WebDriver user2 = CustomKeywords.'browser.newWindow.open'()

DriverFactory.changeWebDriver(user2)

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            6), ('username') : findTestData('Login Credentials').getValue('Username', 6)], FailureHandling.STOP_ON_FAILURE)

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_comment list 1 Reply button'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_comment reply text area'), 'test reply')

WebUI.click(findTestObject('Page_foi.flow/comment/button_reply 1_postBtn'), FailureHandling.STOP_ON_FAILURE)

DriverFactory.changeWebDriver(user1)

WebUI.refresh()

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Comment 1 Reply_actionsBtn'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/comment/button_comment Delete'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment delete modal message'), 'Parent comments with a reply cannot be deleted. You may edit the comment.')

WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/comment/button_Delete comment modal confirm'), FailureHandling.STOP_ON_FAILURE)

user1.close()

user2.close()

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

