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

WebUI.callTestCase(findTestCase('helper/foi-test-login'), [('password') : findTestData('Login Credentials').getValue('Password', 
            10), ('username') : findTestData('Login Credentials').getValue('Username', 10)], FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), requestID)

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division dropdown'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/li_Deputy Ministers Office'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/tacs/li_Sport and Creative Sector'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/li_Management Services'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/tacs/li_Arts  Culture'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/li_Ministers Office'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/division dropdown options/tacs/li_Tourism Sector Strategy'), 
    0)

WebUI.click(findTestObject('Page_foi.flow/form/closing modal/div_close dropdown'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/div_ministry division stage'))

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Clarification'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Assigned to Division'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Awaiting Fees'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Fees Received'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Gathering Records'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Records Received'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Awaiting Harms'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Harms Received'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Pending Sign Off'), 
    0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_No Records Response'), 
    0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/stage dropdown options/li_Clarification'), 
    FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/button_Add division to track'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/button_Add division to track'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/button_Add division to track'), FailureHandling.STOP_ON_FAILURE)

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/button_Save'), 0)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/button_Add division to track'), FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/button_Add division to track'), FailureHandling.STOP_ON_FAILURE)

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/ministry view/form/divisional tracking/button_Add division to track'), 
    0)

WebUI.click(findTestObject('Page_foi.flow/navbar/button_Sign Out'))

//WebUI.acceptAlert(FailureHandling.STOP_ON_FAILURE)

