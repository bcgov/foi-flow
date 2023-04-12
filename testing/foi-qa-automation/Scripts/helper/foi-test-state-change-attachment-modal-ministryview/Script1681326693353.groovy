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

//WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)
WebUI.verifyElementPresent(findTestObject('Page_foi.flow/form/state change dialog/button_Cancel'), 0)

WebUI.verifyElementAttributeValue(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), 'accept', 
    'application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword,.xls,.xlsx,.doc,.docx', 
    0)

WebUI.verifyElementNotHasAttribute(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), 'multiple', 
    0, FailureHandling.STOP_ON_FAILURE)

WebUI.click(findTestObject('Page_foi.flow/attachment/button_Add Files'))

//
WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/50mb.pdf')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/li_uploaded attachment 1'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/p_File over 50 mb error'), 0)

//WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)
WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() + 
    '/Test Attachments/download.png')

WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/li_uploaded attachment 1'), 0)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/p_File invalid type state change'), 0)

//WebUI.verifyElementNotClickable(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)
WebUI.verifyElementClickable(findTestObject('Page_foi.flow/attachment/button_Add Files'), FailureHandling.STOP_ON_FAILURE)

WebUI.uploadFile(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), (RunConfiguration.getProjectDir() + 
    '/Test Attachments/') + filename)

WebUI.verifyElementPresent(findTestObject('Page_foi.flow/attachment/Page_ABC-2099-3924/span_test2.docx'), 0)

WebUI.verifyElementText(findTestObject('Page_foi.flow/attachment/Page_ABC-2099-3924/span_test2.docx'), filename)

//WebUI.uploadFileWithDragAndDrop(findTestObject('Page_foi.flow/attachment/input_Add Files_file-upload-input'), RunConfiguration.getProjectDir() +
//    '/Test Attachments/test2.docx', FailureHandling.STOP_ON_FAILURE)
//WebUI.verifyElementClickable(findTestObject('Page_foi.flow/form/state change dialog/button_Continue'), FailureHandling.STOP_ON_FAILURE)
WebUI.verifyElementNotPresent(findTestObject('Page_foi.flow/attachment/button_Add Files'), 0)

