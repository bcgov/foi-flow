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
import groovy.json.JsonSlurper as JsonSlurper

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/button_Watch'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Watch')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/i_Watch eye icon'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '0')

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/i_Watch user icon'), 0)

WebUI.click(findTestObject('Page_foi.flow/form/watch/button_Watch'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Unwatch')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Unwatch')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.click(findTestObject('Page_foi.flow/form/watch/button_Unwatch'))

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '0')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Watch')

WebUI.refresh()

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '0')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Watch')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Watch')

WebUI.click(findTestObject('Page_foi.flow/form/watch/div_add other watchers'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/watch/div_watch dropdown popup'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Intake Team'), 0)

//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Business Team'), 0)
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Central Team'), 0)
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_MCFD Personals Team'), 0)
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Social Tech Team'), 0)
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Resource Team'), 0)
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Business Team'), 0)
//
//WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Processing Team'), 0)
WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/assignee dropdown/li_Flex Team'), 0)

WebUI.verifyElementNotHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate]), 'aria-selected', 
    0, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate]))

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : teammate]), 'aria-selected', 'true', 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.verifyElementNotHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + 
            firstname]), 'aria-selected', 0, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + firstname]), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + 
            firstname]), 'aria-selected', 'true', 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '2')

WebUI.click(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + firstname]), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotHasAttribute(findTestObject('Page_foi.flow/form/assignee dropdown/li_assignee user option', [('user') : (lastname + ', ') + 
            firstname]), 'aria-selected', 0, FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_close dropdown'))

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/form/watch/div_watch dropdown popup'), 0)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('New Test Data').getValue('Password', 
            6), ('username') : findTestData('New Test Data').getValue('Username', 6)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_Watching Requests'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/queue/div_request queue row 1'), 0)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/span_Watch Counter'), '1')

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/watch/button_Watch'), 'Unwatch')

@com.kms.katalon.core.annotation.SetUp
def setup() {
    def response = WS.sendRequest(findTestObject('FoiRawRequest'))

    def jsonSlurper = new JsonSlurper()

    requestID = jsonSlurper.parseText(response.responseText).id.toString()

    WS.verifyResponseStatusCode(response, 200)

    WebUI.openBrowser(GlobalVariable.BASE_URL)

    WebUI.callTestCase(findTestCase('helper/foi-test-login'), [:], FailureHandling.STOP_ON_FAILURE)
}

