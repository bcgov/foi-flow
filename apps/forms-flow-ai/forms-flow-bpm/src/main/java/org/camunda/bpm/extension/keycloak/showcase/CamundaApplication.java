package org.camunda.bpm.extension.keycloak.showcase;

import org.camunda.bpm.engine.AuthorizationService;
import org.camunda.bpm.engine.ProcessEngine;
import org.camunda.bpm.engine.ProcessEngines;
import org.camunda.bpm.engine.authorization.Authorization;
import org.camunda.bpm.engine.authorization.Resources;
import org.camunda.bpm.extension.commons.connector.AccessHandlerFactory;
import org.camunda.bpm.spring.boot.starter.annotation.EnableProcessApplication;
import org.camunda.bpm.spring.boot.starter.event.PostDeployEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.FactoryBean;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.config.ServiceLocatorFactoryBean;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.PropertySource;
import org.springframework.context.event.EventListener;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.security.oauth2.config.annotation.web.configuration.EnableOAuth2Client;


import javax.sql.DataSource;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import static org.camunda.bpm.engine.authorization.Permissions.ALL;
import static org.camunda.bpm.engine.authorization.Authorization.ANY;
import static org.camunda.bpm.engine.authorization.Authorization.AUTH_TYPE_GRANT;

/**
 * The Camunda Showcase Spring Boot application.
 */
@EnableOAuth2Client
@EnableConfigurationProperties
@PropertySource("application.yaml")
@SpringBootApplication(scanBasePackages = {"org.camunda.bpm.extension"})
@EnableProcessApplication("camunda.showcase")
public class CamundaApplication {

	/** This class' logger. */
	private static final Logger LOG = LoggerFactory.getLogger(CamundaApplication.class);

	/**
	 * Post deployment work.
	 * @param event
	 */
	@EventListener
	public void onPostDeploy(PostDeployEvent event) {
		LOG.info("========================================");
		LOG.info("Successfully started Camunda Showcase");
		LOG.info("========================================\n");
		authorizeServiceAccount();
	}

	/**
	 * Starts this application.
	 * @param args arguments
	 */
	public static void main(String... args) {
		SpringApplication.run(CamundaApplication.class, args);
	}

	/**
	 * Primary datasource.
	 * This is owned by Camunda.
	 * Note: Bean name should not be changed.
	 * @return
	 */
	@Bean(name="camundaBpmDataSource")
	@ConfigurationProperties("spring.datasource")
	@Primary
	public DataSource camundaBpmDataSource(){
		return DataSourceBuilder.create().build();
	}

	@Bean("bpmJdbcTemplate")
	public NamedParameterJdbcTemplate bpmJdbcTemplate(@Qualifier("camundaBpmDataSource") DataSource camundaBpmDataSource) {
		return new NamedParameterJdbcTemplate(camundaBpmDataSource);
	}

	@Bean
	@ConfigurationProperties(prefix = "security.oauth2.client")
	public Properties clientCredentialProperties() {
		return new Properties();
	}

	@Bean
	@ConfigurationProperties(prefix = "formsflow.ai")
	public Properties integrationCredentialProperties() {
		return new Properties();
	}

	@Bean("accessHandlerFactory")
	public FactoryBean accessHandlerFactory() {
		ServiceLocatorFactoryBean factoryBean = new ServiceLocatorFactoryBean();
		factoryBean.setServiceLocatorInterface(AccessHandlerFactory.class);
		return factoryBean;
	}


	private static void authorizeServiceAccount() {
		LOG.info("Setting authorization for service account...");
		String serviceAccountId = "service-account-"+System.getenv("KEYCLOAK_CLIENTID");
		ProcessEngine processEngine = ProcessEngines.getDefaultProcessEngine();
		AuthorizationService authorizationService = processEngine.getAuthorizationService();
		List<Authorization> authorizationList = authorizationService.createAuthorizationQuery().userIdIn(serviceAccountId).list();
		List<Integer> existingPermissions = new ArrayList<>();
		for(Authorization entry: authorizationList) {
			if(getAServiceAccountPermissions().contains(entry.getResourceType()) && !existingPermissions.contains(entry.getResourceType())) {
					existingPermissions.add(entry.getResourceType());
			}
		}
		for(Integer permission: getAServiceAccountPermissions()) {
				if(!existingPermissions.contains(permission)) {
					Authorization auth = authorizationService.createNewAuthorization(AUTH_TYPE_GRANT);
					auth.setUserId(serviceAccountId);
					auth.setResourceType(permission);
					auth.setResourceId(ANY);
					auth.addPermission(ALL);
					authorizationService.saveAuthorization(auth);
				}
		}
		LOG.info("Authorization set!\n");
	}

	private static List<Integer> getAServiceAccountPermissions() {
		List<Integer> permissions = new ArrayList<>();
		permissions.add(Resources.DEPLOYMENT.resourceType());
		permissions.add(Resources.PROCESS_DEFINITION.resourceType());
		permissions.add(Resources.DECISION_DEFINITION.resourceType());
		permissions.add(Resources.PROCESS_INSTANCE.resourceType());
		permissions.add(Resources.TASK.resourceType());
		return permissions;
	}
}
