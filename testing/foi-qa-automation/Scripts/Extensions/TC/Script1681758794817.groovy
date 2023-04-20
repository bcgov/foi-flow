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

WebUI.openBrowser('')

WebUI.navigateToUrl('https://dev.foirequests.gov.bc.ca/')

WebUI.click(findTestObject('null'))

WebUI.setText(findTestObject('null'), 'foiintakeflex@idir')

WebUI.setEncryptedText(findTestObject('null'), '4fqcoPhx3Nk=')

WebUI.sendKeys(findTestObject('null'), Keys.chord(
        Keys.ENTER))



WebUI.click(findTestObject('Page_foi.flow/queue/div_My Team Requests'))

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.setText(findTestObject('Page_foi.flow/queue/input_Dashboard Filter'), 'ABC-2099-5560')

WebUI.delay(GlobalVariable.DEFAULT_TIMEOUT)

WebUI.click(findTestObject('Page_foi.flow/queue/div_request queue row 1'))

WebUI.scrollToElement(findTestObject('Page_foi.flow/form/inputs/request details/Page_ABC-2099-7654195/input_Legislated Due Date_dueDate'),
	0)

def ldd = WebUI.getAttribute(findTestObject('Page_foi.flow/form/inputs/request details/Page_ABC-2099-7654195/input_Legislated Due Date_dueDate'),
	'value').toString()
println(ldd)


//def (name,mon,value) = ldd.split('-')
def mon=ldd.split('-')[1]
def arrmon = ldd.split('-')
//println(arrmon.length)
//def mon = arrmon[1]

println(arrmon[0].toString())
println(arrmon[1].toString())
println(arrmon[2].toString())
def month=''
if (mon == '01') {
	 month = 'Jan'
	
}

if (mon == '02') {
	 month = 'Feb'
	
}

if (mon == '03') {
	 month = 'Mar'
	
}

if (mon == '04') {
	 month = 'Apr'
	
}

if (mon == '05') {
	 month = 'May'
	
}

if (mon == '06') {
	 month = 'Jun'
	
}

if (mon == '07') {
	 month = 'Jul'
	
}

if (mon == '08') {
	 month = 'Aug'
	
}

if (mon == '09') {
	month = 'Sep'
   
}
println(month)

def newldddate = Date.parse('yyyy-MM-dd', ldd).format('MM/dd/yyyy')

def date1 = newldddate.split('/')[1]

def year1 = newldddate.split('/')[2]



