package browser

import org.openqa.selenium.WebDriver
import org.openqa.selenium.chrome.ChromeDriver
import org.openqa.selenium.chrome.ChromeOptions
import org.openqa.selenium.edge.EdgeDriver
import org.openqa.selenium.edge.EdgeOptions
import org.openqa.selenium.firefox.FirefoxDriver
import org.openqa.selenium.firefox.FirefoxOptions

import com.kms.katalon.core.annotation.Keyword
import com.kms.katalon.core.configuration.RunConfiguration
import com.kms.katalon.core.webui.driver.DriverFactory as DriverFactory


public class newWindow {
	@Keyword
	def open() {
		String driverProp = RunConfiguration.getExecutionProperties().get("drivers").get("system").get("WebUI").get("browserType")
		println  driverProp
		
		switch (driverProp) {
			case "CHROME_DRIVER":
				System.setProperty('webdriver.chrome.driver', DriverFactory.getChromeDriverPath())
				WebDriver driver = new ChromeDriver(new ChromeOptions())
				return driver
			case  "EDGE_CHROMIUM_DRIVER":
				System.setProperty('webdriver.edge.driver', DriverFactory.getEdgeChromiumDriverPath())
				WebDriver driver = new EdgeDriver(new EdgeOptions())
				return driver
			case  "FIREFOX_DRIVER":
				System.setProperty('webdriver.firefox.driver', DriverFactory.getGeckoDriverPath())
				WebDriver driver = new FirefoxDriver(new FirefoxOptions())
				return driver
			default:
				throw new Exception("Unexpected browser type")
			
		}

	}
}
