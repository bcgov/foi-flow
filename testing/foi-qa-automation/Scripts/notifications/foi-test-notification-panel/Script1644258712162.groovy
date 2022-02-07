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

WebUI.callTestCase(findTestCase('submit/foi-test-save-request-form'), [('password') : findTestData('New Test Data').getValue(
            'Password', 2), ('username') : findTestData('New Test Data').getValue('Username', 2), ('firstname') : findTestData(
            'New Test Data').getValue('First Name', 2), ('lastname') : findTestData('New Test Data').getValue('Last Name', 
            2)], FailureHandling.STOP_ON_FAILURE)

WebDriver user1 = DriverFactory.getWebDriver()

WebDriver user2 = CustomKeywords.'browser.newWindow.open'()

DriverFactory.changeWebDriver(user2)

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('New Test Data').getValue('Password', 
            6), ('username') : findTestData('New Test Data').getValue('Username', 6)], FailureHandling.STOP_ON_FAILURE)

assert WebUI.getAttribute(findTestObject('Page_foi.flow/span_notification indicator'), 'class').contains('MuiBadge-invisible')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/div_notification popup'), 0)

WebUI.click(findTestObject('Page_foi.flow/notification bell'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/div_notification popup'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/div_notification list 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/notification bell'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/div_notification popup'), 0)

DriverFactory.changeWebDriver(user1)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/div_Assigned'))

WebUI.click(findTestObject('Page_foi.flow/li_assignee user option', [('user') : teammate]))

WebUI.scrollToElement(findTestObject('Page_foi.flow/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/button_Save'), FailureHandling.STOP_ON_FAILURE)

DriverFactory.changeWebDriver(user2)

WebUI.refresh()

WebUI.verifyElementVisible(findTestObject('Page_foi.flow/span_notification indicator'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/span_notification indicator'), '1')

WebUI.click(findTestObject('Page_foi.flow/notification bell'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/div_notification list 1'), 0)

