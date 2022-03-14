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
import groovy.json.JsonSlurper as JsonSlurper

WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Search'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment editor'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment editor'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/div_Comment textbox'), FailureHandling.STOP_ON_FAILURE)

WebDriver driver = DriverFactory.getWebDriver()

WebElement focusedElement = driver.switchTo().activeElement()

def objectElement = WebUiCommonHelper.findWebElement(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 1)

assert objectElement == focusedElement

WebUI.click(findTestObject('Page_foi.flow/body'), FailureHandling.STOP_ON_FAILURE)

focusedElement = driver.switchTo().activeElement()

assert objectElement != focusedElement

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/span_comment characters remaining'), '1000 characters remaining')

WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'a')

WebUI.click(findTestObject('Page_foi.flow/body'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'a')

WebUI.verifyElementClickable(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/a_FOI'))

WebUI.verifyAlertPresent(0)

WebUI.acceptAlert(FailureHandling.STOP_ON_FAILURE)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Search'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'a')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/span_comment characters remaining'), '999 characters remaining')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/a_FOI'))

WebUI.verifyAlertPresent(0)

WebUI.dismissAlert(FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'a')

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), Keys.BACK_SPACE.toString())

WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/span_comment characters remaining'), '1000 characters remaining')

def longString = 'q8gXydZTqnCejDznun3MWU1onCRvlQjXWQAti3NQRCtVFVEuP99mGy58pqIknj2VDet5triwfwp5KIOSg5zd7koPLhLQABiBszPfnkVRqRnf1zKpjMcCiXKcCPP2hmQxfdB6TaG8J82ESsqxGcfedQSFLXoN8qfd1OCdIRpdbW81y8hp9U7NHRTv73IPvNUlCpjLnnrcwW5yB9pWH9DvhZJrM8T8KQjdPz76HmTIa3EazElHbZQSbZrZQ9XEeVp8V1HvrsIqmNMHywVuFDLPGWJqCjX1zx4Dutu1Q9EHSvIpieQOnurQxw4Xa9uxVvkt81OrGD8zZ68EB0rOIZLVqYjVwVfCyz9RBNeXYWjgaTq6RsS0E6yFl1i0t8w2FfE0EtlCMW7mtuaLhoiNE5q8bu6jj5ZUWDNm1LPlGOTmzYLyB3r2AR2eDSdD803Z94r62X0ddveI9qlWwb39KQaTRMc8OWXcu0gRUalKPDJn5q8eEqeHmRdHdBsDQzyhghFZd06szJg2ASikLzCvMhrG8VQgnAfgzu2SLvseASGm6gZSnJfEMLJWbySv0dgq5WQXGnfFn8VBY2lv0lJVG4Nx5LMBjJM3Mv7N0PT3VJJUrrxnj6PTICvwJlOXgxq8sJTgwztnXaSExKsapccQ2hAThmGr13h5x4sqzD3ySdFL0CzYsccWJzAwVaHZApTiBuZnhIzGpqI0OT5xZcBhZjP9hXIMesDr23VU2hLAuPoXMP9KtXXqPSfmnswQ0xRdOi84BkTxYmqeENArZeOXWrdv0ClMDJHFm5crxF0qMkLmbbeRAGlBoAlZTextsfvAFiCbB42zji6FtdI0sXFpRkwKLZZdtL0CT7M8pT7rE6kiu5fQkScNdMMYRIJv1Frc2V8ZEi4L2H4PIY40AJLyrKkIl45W7MSI7AKodRPupRPZ7QWEVxEaXBGjjyflxr6XpweusaBW8t9y5qNCdkO'

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), longString)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/span_comment characters remaining'), '25 characters remaining')

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/comment/span_comment characters remaining'), 'color'), 
    'rgba(255, 0, 0, 1)', false)

def remainingString = '2EarUhvAMTvIv1O2Ox9IoOJgG'

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), remainingString)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment textbox'), longString + remainingString)

assert WebUI.getText(findTestObject('Page_foi.flow/comment/div_Comment textbox'), FailureHandling.STOP_ON_FAILURE).length() == 
1000

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'a')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment textbox'), longString + remainingString)

assert WebUI.getText(findTestObject('Page_foi.flow/comment/div_Comment textbox'), FailureHandling.STOP_ON_FAILURE).length() == 
1000

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), Keys.chord(Keys.CONTROL, 'a'))

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), Keys.BACK_SPACE.toString())

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'test comment')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1'), 0)

//def today = new Date()
WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments (1)')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'test comment')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1 date'), 0)

//WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment list 1 date'), today.format('yyyy MMM dd | hh:mm a'))
WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment list 1 user'), (lastname + ', ') + firstname)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'test comment 2')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment list 2'), 0)

//today = new Date()
WebUI.click(findTestObject('Page_foi.flow/comment/button_Post comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments (2)')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 2'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'test comment 2')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 2 text'), 'test comment' //WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment list 2 date'), today.format('yyyy MMM dd | hh:mm a'))
    )

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1 date'), 0)

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)
}

