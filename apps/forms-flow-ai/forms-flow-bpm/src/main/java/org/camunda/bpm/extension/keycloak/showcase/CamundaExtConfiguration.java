package org.camunda.bpm.extension.keycloak.showcase;


import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.boot.context.properties.ConfigurationProperties;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;



import java.util.Properties;


/**
 * Extended Configuration file
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Configuration
public class CamundaExtConfiguration {

	@Bean
	@ConfigurationProperties(prefix = "websocket")
	public Properties messageBrokerProperties() { return new Properties(); }

	@Bean
	public ObjectMapper objectMapper() { return new ObjectMapper(); }

}
