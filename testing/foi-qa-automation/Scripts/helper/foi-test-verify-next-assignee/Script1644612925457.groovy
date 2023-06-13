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

if (requestType == 'general') {
	//WebUI.verifyElementText(findTestObject('Page_foi.flow/form/state change dialog/td_Next Assignee'), 'Flex Team')
	return
}

def jsonSlurper = new JsonSlurper()

def ministryProcessingMap = jsonSlurper.parseText((((((((((((((((((((((((((((((((('{"AEST" : "Social Education",' + '"AGR" : "Resource Team",') + 
    '"BRD" : "Central Team",') + '"CAS" : "Central Team",') + '"MCF" : "MCFD Personals Team",') + '"CLB" : "Social Education",') + 
    '"CITZ" : "Central Team",') + '"EAO" : "Resource Team",') + '"EDU" : "Social Education, Flex Team",') + '"EMBC" : "Justice Health Team",') + 
    '"EMLI" : "Resource Team",') + '"FIN" : "Central Team",') + '"FOR" : "Resource Team",') + '"GCPE" : "Social Education",') + 
    '"HLTH" : "Justice Health Team",') + '"IIO" : "Justice Health Team",') + '"IRR" : "Resource Team",') + '"JERI" : "Business Team",') + 
    '"LBR" : "Business Team",') + '"LDB" : "Justice Health Team",') + '"AG" : "Justice Health Team",') + '"MGC" : "Central Team",') + 
    '"MMHA" : "Justice Health Team",') + '"MUNI" : "Business Team",') + '"ENV" : "Resource Team",') + '"SDPR" : "Social Education",') + 
    '"OBC" : "Central Team",') + '"OCC" : "Justice Health Team",') + '"PREM" : "Central Team",') + '"PSA" : "Social Education",') + 
    '"PSSG" : "Justice Health Team",') + '"TACS" : "Business Team",') + '"TIC" : "Business Team",') + '"TRAN" : "Business Team"}')

if (!(ministryCode)) {
    ministryCode = (WebUI.getText(findTestObject('Page_foi.flow/form/h3_Form Request Title'), FailureHandling.STOP_ON_FAILURE).split(
        '-')[0])
}

println(ministryCode)

WebUI.verifyElementText(findTestObject('Page_foi.flow/form/state change dialog/td_Next Assignee'), ministryProcessingMap[ministryCode])


