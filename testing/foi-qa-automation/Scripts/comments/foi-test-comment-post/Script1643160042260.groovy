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
import java.util.Arrays

// robust disabled detector (handles aria-disabled, classes, CSS, etc.)
def isDisabled = { TestObject btn ->
  try {
	WebElement el = WebUiCommonHelper.findWebElement(btn, 5)
	def disabledProp  = WebUI.executeJavaScript('return !!arguments[0].disabled;', Arrays.asList(el))
	def ariaDisabled  = WebUI.executeJavaScript('return arguments[0].getAttribute("aria-disabled")==="true";', Arrays.asList(el))
	def hasAttribute  = WebUI.executeJavaScript('return arguments[0].hasAttribute("disabled");', Arrays.asList(el))
	def peNone        = WebUI.executeJavaScript('return window.getComputedStyle(arguments[0]).pointerEvents==="none";', Arrays.asList(el))
	def classDisabled = WebUI.executeJavaScript('return (arguments[0].className||"").toLowerCase().includes("disabled");', Arrays.asList(el))
	return (disabledProp || ariaDisabled || hasAttribute || peNone || classDisabled)
  } catch (ignored) { return false }
}

def waitUntilDisabled = { TestObject btn, int timeoutSec = 5 ->
  long end = System.currentTimeMillis() + timeoutSec*1000
  while (System.currentTimeMillis() < end) {
	if (isDisabled(btn)) return true
	WebUI.delay(0.1)
  }
  return false
}

def waitUntilEnabled = { TestObject btn, int timeoutSec = 5 ->
  long end = System.currentTimeMillis() + timeoutSec*1000
  while (System.currentTimeMillis() < end) {
	if (!isDisabled(btn)) return true
	WebUI.delay(0.1)
  }
  return false
}


def confirmUnsavedChangesLeave = {
  // give portal a tick to mount if needed
  WebUI.delay(0.2)

  // 0) If URL already changed (silent nav), just return
  String before = WebUI.getUrl()

  // 1) Native alert/confirm
  if (WebUI.waitForAlert(1, FailureHandling.OPTIONAL)) {
    WebUI.acceptAlert(FailureHandling.STOP_ON_FAILURE)
    return
  }

  // 2) Web modal
  TestObject leaveBtn = new TestObject('runtime_leave_btn')
  leaveBtn.addProperty(
    "xpath",
    com.kms.katalon.core.testobject.ConditionType.EQUALS,
    // Cover most wordings
    "(//button[normalize-space()='Leave' or normalize-space()='Leave page' or normalize-space()='Discard' or @data-testid='confirm-leave' or contains(.,'Leave')])[1]"
  )

  TestObject dialog = new TestObject('runtime_dialog')
  dialog.addProperty(
    "xpath",
    com.kms.katalon.core.testobject.ConditionType.EQUALS,
    "//*[@role='dialog' or contains(@class,'Modal') or contains(@class,'overlay')]"
  )

  boolean hasDialog = WebUI.waitForElementPresent(dialog, 2, FailureHandling.OPTIONAL)
  boolean hasLeave  = WebUI.waitForElementPresent(leaveBtn, 2, FailureHandling.OPTIONAL)

  if (hasDialog || hasLeave) {
    WebUI.waitForElementClickable(leaveBtn, 5)
    WebUI.click(leaveBtn)
    return
  }

  // 3) No alert & no modal → check if navigation already happened
  WebUI.delay(0.2)
  String after = WebUI.getUrl()
  if (before != after) {
    // silently navigated; proceed
    return
  }

  // Nothing happened → fail clearly for investigation
  WebUI.comment('confirmUnsavedChangesLeave: No alert, no modal, and URL unchanged.')
  assert false : 'Expected unsaved-changes confirmation, but none appeared.'
}

def confirmUnsavedChangesStay = {
  WebUI.delay(0.2)
  if (WebUI.waitForAlert(1, FailureHandling.OPTIONAL)) {
    WebUI.dismissAlert(FailureHandling.STOP_ON_FAILURE)
    return
  }

  TestObject stayBtn = new TestObject('runtime_stay_btn')
  stayBtn.addProperty(
    "xpath",
    com.kms.katalon.core.testobject.ConditionType.EQUALS,
    "(//button[normalize-space()='Stay' or normalize-space()='Stay on page' or normalize-space()='Cancel' or @data-testid='confirm-stay' or contains(.,'Stay')])[1]"
  )

  TestObject dialog = new TestObject('runtime_dialog')
  dialog.addProperty(
    "xpath",
    com.kms.katalon.core.testobject.ConditionType.EQUALS,
    "//*[@role='dialog' or contains(@class,'Modal') or contains(@class,'overlay')]"
  )

  if (WebUI.waitForElementPresent(dialog, 3, FailureHandling.OPTIONAL)
      || WebUI.waitForElementPresent(stayBtn, 3, FailureHandling.OPTIONAL)) {
    WebUI.waitForElementClickable(stayBtn, 5)
    WebUI.click(stayBtn)
    return
  }

  // If no modal/alert, assume the app kept us on the page anyway
  WebUI.comment('confirmUnsavedChangesStay: No alert or modal; proceeding.')
}


import com.kms.katalon.core.testobject.ConditionType
import com.kms.katalon.core.testobject.TestObject

TestObject postBtn = new TestObject('runtime_post_btn')
postBtn.addProperty(
  "xpath",
  ConditionType.EQUALS,
  // anchor on container + class + type + contains text
  "//div[contains(@class,'newCommentInputActions')]//button[contains(@class,'btn-save') and @type='button' and contains(normalize-space(.),'Post Comment')]"
)

def reopenCommentsAndWait = {
	WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'))
	// ensure editor exists before we look for the button
	WebUI.waitForElementPresent(findTestObject('Page_foi.flow/comment/div_Comment editor'), 10)
	WebUI.waitForElementPresent(postBtn, 10)
	WebUI.scrollToElement(postBtn, 2)
  }
  



WebUI.openBrowser(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.maximizeWindow()

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments (0)')

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

TestObject editor = findTestObject('Page_foi.flow/comment/div_Comment textbox')

//TestObject postBtn = findTestObject('Page_foi.flow/comment/button_Post comment')

// should start DISABLED
assert waitUntilDisabled(postBtn, 5) : 'Expected Post button to be disabled'

assert isDisabled(postBtn)

// type 'a' -> ENABLED
WebUI.sendKeys(editor, 'a')

WebUI.sendKeys(editor, Keys.chord(Keys.TAB))

WebUI.delay(0.2)

assert !(isDisabled(postBtn))

WebUI.waitForElementClickable(postBtn, 5)

// NAV AWAY (leave)
not_run: WebUI.click(findTestObject('Page_foi.flow/form/sidebar/a_FOI'))

not_run: confirmUnsavedChangesLeave()

WebUI.verifyMatch(
  WebUI.getText(findTestObject('Page_foi.flow/comment/span_comment characters remaining')),
  '(999|1000) characters remaining',
  true
)

WebUI.click(editor)
WebUI.sendKeys(editor, Keys.BACK_SPACE.toString())
assert waitUntilDisabled(postBtn, 5) : 'Expected Post button to be disabled'

assert isDisabled(postBtn)

WebUI.sendKeys(editor, 'a')

WebUI.sendKeys(editor, Keys.chord(Keys.TAB))

WebUI.delay(0.2)

WebUI.verifyElementText(editor, 'a')

assert !(isDisabled(postBtn))

WebUI.waitForElementClickable(postBtn, 5)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/a_FOI'))

not_run: confirmUnsavedChangesLeave()

WebUI.callTestCase(findTestCase('helper/foi-test-advanced-search-by-id'), [('requestID') : requestID], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'a')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/span_comment characters remaining'), '999 characters remaining')

not_run: WebUI.click(findTestObject('Page_foi.flow/form/sidebar/a_FOI'))

not_run: confirmUnsavedChangesStay()

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment textbox'), 'a')

WebUI.sendKeys(findTestObject('Page_foi.flow/comment/div_Comment textbox'), Keys.BACK_SPACE.toString())

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/span_comment characters remaining'), '1000 characters remaining')

assert waitUntilDisabled(postBtn, 5) : 'Expected Post button to be disabled'

assert isDisabled(postBtn)

def longString = 'q8gXydZTqnCejDznun3MWU1onCRvlQjXWQAti3NQRCtVFVEuP99mGy58pqIknj2VDet5triwfwp5KIOSg5zd7koPLhLQABiBszPfnkVRqRnf1zKpjMcCiXKcCPP2hmQxfdB6TaG8J82ESsqxGcfedQSFLXoN8qfd1OCdIRpdbW81y8hp9U7NHRTv73IPvNUlCpjLnnrcwW5yB9pWH9DvhZJrM8T8KQjdPz76HmTIa3EazElHbZQSbZrZQ9XEeVp8V1HvrsIqmNMHywVuFDLPGWJqCjX1zx4Dutu1Q9EHSvIpieQOnurQxw4Xa9uxVvkt81OrGD8zZ68EB0rOIZLVqYjVwVfCyz9RBNeXYWjgaTq6RsS0E6yFl1i0t8w2FfE0EtlCMW7mtuaLhoiNE5q8bu6jj5ZUWDNm1LPlGOTmzYLyB3r2AR2eDSdD803Z94r62X0ddveI9qlWwb39KQaTRMc8OWXcu0gRUalKPDJn5q8eEqeHmRdHdBsDQzyhghFZd06szJg2ASikLzCvMhrG8VQgnAfgzu2SLvseASGm6gZSnJfEMLJWbySv0dgq5WQXGnfFn8VBY2lv0lJVG4Nx5LMBjJM3Mv7N0PT3VJJUrrxnj6PTICvwJlOXgxq8sJTgwztnXaSExKsapccQ2hAThmGr13h5x4sqzD3ySdFL0CzYsccWJzAwVaHZApTiBuZnhIzGpqI0OT5xZcBhZjP9hXIMesDr23VU2hLAuPoXMP9KtXXqPSfmnswQ0xRdOi84BkTxYmqeENArZeOXWrdv0ClMDJHFm5crxF0qMkLmbbeRAGlBoAlZTextsfvAFiCbB42zji6FtdI0sXFpRkwKLZZdtL0CT7M8pT7rE6kiu5fQkScNdMMYRIJv1Frc2V8ZEi4L2H4PIY40AJLyrKkIl45W7MSI7AKodRPupRPZ7QWEVxEaXBGjjyflxr6XpweusaBW8t9y5qNCdkO'

WebUI.sendKeys(editor, longString)

WebUI.sendKeys(editor, Keys.chord(Keys.TAB))

WebUI.delay(0.2)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/span_comment characters remaining'), '25 characters remaining')

WebUI.verifyMatch(WebUI.getCSSValue(findTestObject('Page_foi.flow/comment/span_comment characters remaining'), 'color'), 
    'rgba(255, 0, 0, 1)', false)

def remainingString = '2EarUhvAMTvIv1O2Ox9IoOJgG'

WebUI.sendKeys(editor, remainingString)

WebUI.sendKeys(editor, Keys.chord(Keys.TAB))

WebUI.delay(0.2)

WebUI.verifyElementText(editor, longString + remainingString)

assert WebUI.getText(editor, FailureHandling.STOP_ON_FAILURE).length() == 1000

WebUI.sendKeys(editor, 'a')

WebUI.sendKeys(editor, Keys.chord(Keys.TAB))

WebUI.delay(0.2)

WebUI.verifyElementText(editor, longString + remainingString)

assert WebUI.getText(editor, FailureHandling.STOP_ON_FAILURE).length() == 1000

WebUI.sendKeys(editor, Keys.chord(Keys.CONTROL, 'a'))

WebUI.sendKeys(editor, Keys.BACK_SPACE.toString())

WebUI.sendKeys(editor, Keys.chord(Keys.TAB))

WebUI.delay(0.2 // commit empty -> disabled flips reliably
    )

WebUI.sendKeys(editor, 'test comment')

WebUI.sendKeys(editor, Keys.chord(Keys.TAB))

WebUI.delay(0.2 // commit filled -> enabled flips reliably
    )

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1'), 0)

//def today = new Date()
assert waitUntilEnabled(postBtn, 5) : 'Post should be enabled before click'
WebUI.scrollToElement(postBtn, 2)
WebUI.waitForElementClickable(postBtn, 5)
WebUI.click(postBtn, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), 'Comments (1)')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'test comment')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1 date'), 0)

//WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment list 1 date'), today.format('yyyy MMM dd | hh:mm a'))
WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment list 1 user'), (lastname + ', ') + firstname)

WebUI.click(findTestObject('Page_foi.flow/comment/button_Add Comment'), FailureHandling.STOP_ON_FAILURE)

WebUI.sendKeys(editor, 'test comment 2')

WebUI.sendKeys(editor, Keys.chord(Keys.TAB))

WebUI.delay(0.2)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/comment/div_Comment list 2'), 0)

//today = new Date()
assert waitUntilEnabled(postBtn, 10) : 'Post should be enabled before click'
WebUI.scrollToElement(postBtn, 2)
WebUI.waitForElementClickable(postBtn, 5)

WebUI.click(postBtn, FailureHandling.STOP_ON_FAILURE)

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

