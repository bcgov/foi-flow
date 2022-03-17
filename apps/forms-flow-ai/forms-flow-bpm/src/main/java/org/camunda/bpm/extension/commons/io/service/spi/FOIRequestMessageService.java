package org.camunda.bpm.extension.commons.io.service.spi;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.camunda.bpm.extension.commons.connector.HTTPServiceInvoker;
import org.camunda.bpm.extension.commons.io.message.spi.FOIRequestMessage;
import org.camunda.bpm.engine.rest.dto.VariableValueDto;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.config.ConfigurableBeanFactory;
import org.springframework.context.annotation.Scope;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Service component for FOI message listener.
 * This class creates workflow instance for the predefined process definition.
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Qualifier("foiRequestMessageService")
@Component
public class FOIRequestMessageService {

    private final Logger LOGGER = Logger.getLogger(FOIRequestMessageService.class.getName());

    @Autowired
    private HTTPServiceInvoker httpServiceInvoker;

    @Autowired
    private Properties integrationCredentialProperties;

    @Autowired
    private ObjectMapper objectMapper;


    public void execute(FOIRequestMessage message) {
        try {
            System.out.println(getUrl(message.getProcessDefinitionKey());
            httpServiceInvoker.execute(getUrl(message.getProcessDefinitionKey()), HttpMethod.POST, prepareCreateProcessInstanceRequest(message.getAttributes()));
        } catch (JsonProcessingException e) {
            LOGGER.log(Level.SEVERE,"Exception occurred in created instance",e);
        }
    }

    private String getUrl(String processDefinitionKey) {
        System.out.println("**********************");
        System.out.println(processDefinitionKey);
        return integrationCredentialProperties.getProperty("workflow.url")+"/process-definition/key/"+processDefinitionKey+"/start";
    }

    private VariableValueDto prepareVariable(String key, Object value) {
        VariableValueDto variable = new VariableValueDto();
        variable.setValue(value);
        return variable;
    }

    private  String prepareCreateProcessInstanceRequest(Map<String, Object> data) throws JsonProcessingException {
        Map<String, VariableValueDto> variables = new HashMap();
        for(Map.Entry<String, Object> entry : data.entrySet()) {
            variables.put(entry.getKey(), prepareVariable(entry.getKey(), entry.getValue()));
        }
        ProcessInstanceRequest reqObj = new ProcessInstanceRequest();
        reqObj.setVariables(variables);
        return objectMapper.writeValueAsString(reqObj);
    }


    @Component
    @Scope(value = ConfigurableBeanFactory.SCOPE_PROTOTYPE)
    @Data
    @NoArgsConstructor
    class ProcessInstanceRequest {
        private Map<String, VariableValueDto> variables;
    }


}
