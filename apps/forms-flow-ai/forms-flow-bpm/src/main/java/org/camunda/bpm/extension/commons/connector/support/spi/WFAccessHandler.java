package org.camunda.bpm.extension.commons.connector.support.spi;

import org.camunda.bpm.extension.commons.connector.support.IAccessHandler;
import org.camunda.bpm.extension.keycloak.rest.RestApiSecurityConfigurationProperties;
import org.springframework.beans.factory.annotation.Autowired;

import org.springframework.context.ApplicationContext;
import org.springframework.http.*;
import org.springframework.security.oauth2.client.OAuth2RestTemplate;
import org.springframework.security.oauth2.client.token.grant.client.ClientCredentialsResourceDetails;
import org.springframework.stereotype.Service;

import javax.inject.Inject;
import java.util.Properties;
import java.util.logging.Logger;

/**
 * This handler component is delegated for any engine specific rest based calls.
 * The component uses client credentials based oauth token.
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Service("wfAccessHandler")
public class WFAccessHandler implements IAccessHandler {
    private final Logger LOGGER = Logger.getLogger(WFAccessHandler.class.getName());

    @Inject
    private RestApiSecurityConfigurationProperties configProps;

    @Inject
    private ApplicationContext applicationContext;

    @Autowired
    private Properties clientCredentialProperties;

    public ResponseEntity<String> exchange(String url, HttpMethod method, String payload) {
        //HTTP Headers
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Authorization", "Bearer " + getOAuth2RestTemplate().getAccessToken());
        HttpEntity<String> reqObj =
                new HttpEntity<String>(payload, headers);

        ResponseEntity<String> wrsp = getOAuth2RestTemplate().exchange(url, method, reqObj, String.class);
        LOGGER.info("Response code for service invocation: " + wrsp.getStatusCode());
        return wrsp;
    }

    private OAuth2RestTemplate getOAuth2RestTemplate() {
        ClientCredentialsResourceDetails resourceDetails = new ClientCredentialsResourceDetails ();
        resourceDetails.setClientId(applicationContext.getEnvironment().getRequiredProperty("spring.security.oauth2.client.registration." + configProps.getProvider() + ".client-id"));
        resourceDetails.setClientSecret(applicationContext.getEnvironment().getRequiredProperty("spring.security.oauth2.client.registration." + configProps.getProvider() + ".client-secret"));
        resourceDetails.setAccessTokenUri(applicationContext.getEnvironment().getRequiredProperty("spring.security.oauth2.client.registration." + configProps.getProvider() + ".accessTokenUri"));
        resourceDetails.setGrantType("client_credentials");
        return new OAuth2RestTemplate(resourceDetails);
    }

}
