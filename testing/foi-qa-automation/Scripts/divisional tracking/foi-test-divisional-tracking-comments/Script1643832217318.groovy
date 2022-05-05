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

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            8), ('username') : findTestData('Login Credentials').getValue('Username', 8)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/div_ministry assigned to'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/ministry assignee/li_ministry assignee foiedu, foiedu'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division dropdown'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/li_Deputy Ministers Office'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division stage'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Clarification'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

WebDriver ministryUser = DriverFactory.getWebDriver()

WebDriver IAOuser = CustomKeywords.'browser.newWindow.open'()

DriverFactory.changeWebDriver(IAOuser)

WebUI.navigateToUrl(GlobalVariable.BASE_URL)

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_queue header ID NUMBER'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_queue header ID NUMBER'))

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), 'EDU-' + requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 1 division'), 'Deputy Minister’s Office')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 1 stage'), 'Clarification')

DriverFactory.changeWebDriver(ministryUser)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'Deputy Minister’s Office division has been added with stage Clarification')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment list 1 user'), 'Request History')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1 date'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'), FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division stage'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Assigned to Division'), 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

DriverFactory.changeWebDriver(IAOuser)

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 1 division'), 'Deputy Minister’s Office')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 1 stage'), 'Assigned to Division')

DriverFactory.changeWebDriver(ministryUser)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'Deputy Minister’s Office division has been updated to stage Assigned to Division')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/div_Comment list 1 user'), 'Request History')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/comment/div_Comment list 1 date'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'), FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division dropdown'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/educ/li_Education Programs'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

DriverFactory.changeWebDriver(IAOuser)

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 1 division'), 'Education Programs')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 1 stage'), 'Assigned to Division')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 2 division'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 2 stage'), 0)

DriverFactory.changeWebDriver(ministryUser)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 2 text'), 'Education Programs division has been added with stage Assigned to Division')

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'Deputy Minister’s Office division with stage Assigned to Division has been removed')

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Request'), FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/button_Add division to track'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division dropdown row 2'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/li_Ministers Office'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division stage row 2'))

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Clarification'), FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

DriverFactory.changeWebDriver(IAOuser)

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 1 division'), 'Education Programs')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 1 stage'), 'Assigned to Division')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 2 division'), 'Minister’s Office')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 2 stage'), 'Clarification')

DriverFactory.changeWebDriver(ministryUser)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/i_Division stage row 2 delete'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/button_Save'), FailureHandling.STOP_ON_FAILURE)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/sidebar/div_Sidebar Comments'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/comment/p_comment list 1 text'), 'Minister’s Office division with stage Clarification has been removed')

DriverFactory.changeWebDriver(IAOuser)

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 1 division'), 'Education Programs')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 1 stage'), 'Assigned to Division')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 2 division'), 0)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/div_divison tracking iao view row 2 stage'), 0)

ministryUser.close()

IAOuser.close()

