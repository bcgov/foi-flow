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
import org.openqa.selenium.WebDriver as WebDriver
import com.kms.katalon.core.webui.driver.DriverFactory as DriverFactory

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Open'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

requestID = WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE)

WebDriver user1 = DriverFactory.getWebDriver()

WebDriver user2 = CustomKeywords.'browser.newWindow.open'()

DriverFactory.changeWebDriver(user2)

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('New Test Data').getValue('Password', 
            6), ('username') : findTestData('New Test Data').getValue('Username', 6)], FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification popup'), 0)

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/notification bell'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification popup'), 0)

if (WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1'), 1, FailureHandling.OPTIONAL)) {
    WebUI.click(findTestObject('Page_foi.flow/navbar/notification/div_notifiation Dismiss All'))
}

assert WebUI.getAttribute(findTestObject('Page_foi.flow/navbar/notification/span_notification indicator'), 'class').contains('MuiBadge-invisible')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/notification bell'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification popup'), 0)

DriverFactory.changeWebDriver(user1)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate2]))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/notification bell'))

if (WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1'), 1, FailureHandling.OPTIONAL)) {
    WebUI.click(findTestObject('Page_foi.flow/navbar/notification/div_notifiation Dismiss All'))
}

assert WebUI.getAttribute(findTestObject('Page_foi.flow/navbar/notification/span_notification indicator'), 'class').contains('MuiBadge-invisible')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification popup'), 0)

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/notification bell'))

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

assert WebUI.getAttribute(findTestObject('Page_foi.flow/navbar/notification/span_notification indicator'), 'class').contains('MuiBadge-invisible')

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/notification bell'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/notification bell'))

DriverFactory.changeWebDriver(user2)

WebUI.refresh()

assert !(WebUI.getAttribute(findTestObject('Page_foi.flow/navbar/notification/span_notification indicator'), 'class').contains('MuiBadge-invisible'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/span_notification indicator'), '1')

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/notification bell'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 request id'), requestID)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 message'), 'New Request Assigned to You.')

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 user'), teammate1)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 time'), 0)

DriverFactory.changeWebDriver(user1)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/div_Status'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/status dropdown/li_Call For Records'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/state change dialog/button_Save Change'), FailureHandling.STOP_ON_FAILURE)

DriverFactory.changeWebDriver(user2)

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/span_notification indicator'), '2')

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/notification bell'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 2'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 message'), 'Moved to Call For Records State')

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 request id'), requestID)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 2 message'), 'New Request Assigned to You.')

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 2 request id'), requestID)

DriverFactory.changeWebDriver(user1)

user1.close()

def requestID2 = WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate2]))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

DriverFactory.changeWebDriver(user2)

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/span_notification indicator'), '3')

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/notification bell'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 request id'), 'U-00' + requestID2)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 message'), 'New Request Assigned to You.')

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/i_notification list 2 delete'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 request id'), 'U-00' + requestID2)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1 message'), 'New Request Assigned to You.')

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 2 request id'), requestID)

WebUI.verifyElementText(findTestObject('Page_foi.flow/navbar/notification/div_notification list 2 message'), 'New Request Assigned to You.')

WebUI.click(findTestObject('Page_foi.flow/navbar/notification/div_notifiation Dismiss All'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 1'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/navbar/notification/div_notification list 2'), 0)

user2.close()

