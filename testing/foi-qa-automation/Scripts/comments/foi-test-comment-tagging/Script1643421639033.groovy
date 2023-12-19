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
import org.openqa.selenium.WebElement as WebElement
import com.kms.katalon.core.webui.common.WebUiCommonHelper as WebUiCommonHelper
import org.openqa.selenium.By as By
import groovy.json.JsonSlurper as JsonSlurper
import org.openqa.selenium.StaleElementReferenceException

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment editor'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment tagging popup'), 0)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), '@')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment tagging popup'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Tagging option 1'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Tagging option 2'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Tagging option 3'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Tagging option 4'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Tagging option 5'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Tagging option 6'), 0)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'm')

def popup = WebUiCommonHelper.findWebElement(findTestObject('Page_foi.flow/comment/div_Comment tagging popup'), 1)

WebUI.delay(8)

List<WebElement> popupChildren = popup.findElements(By.xpath('*'))

println(popupChildren.size())

for (int i = 1; i <= popupChildren.size(); i++) {
    assert WebUI.getText(findTestObject('Page_foi.flow/comment/div_Tagging option ' + i), FailureHandling.STOP_ON_FAILURE).toLowerCase().contains(
        'm')
}

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'a')

//popupChildren = popup.findElements(By.xpath('*'))

//println(popupChildren.size())

//for (int i = 1; i <= popupChildren.size(); i++) {
 //   assert WebUI.getText(findTestObject('Page_foi.flow/comment/div_Tagging option ' + i), FailureHandling.STOP_ON_FAILURE).toLowerCase().contains(
  //      'ma')
//}

//def name = WebUI.getText(findTestObject('Page_foi.flow/comment/div_Tagging option 1'), FailureHandling.STOP_ON_FAILURE)

//WebUI.click(findTestObject('Page_foi.flow/comment/div_Tagging option 1'), FailureHandling.STOP_ON_FAILURE)

//WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment textbox'), name + ' ')

//WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/comment/span_text box Mention'), 'background-color'), 
  //  'rgba(230, 243, 255, 1)', false)

//WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

//WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), name + ' ')

//WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/comment/span_posted comment mention'), 'background-color'), 
  //  'rgba(230, 243, 255, 1)', false)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

