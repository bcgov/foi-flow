package org.camunda.bpm.extension.commons.io.listener.spi;


import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.camunda.bpm.extension.commons.io.listener.TaskEventMessageListener;

import org.camunda.bpm.extension.commons.io.message.spi.FOIRequestMessage;

import org.camunda.bpm.extension.commons.io.service.spi.FOIRequestMessageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;



import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;

/**
 * This SPI specific listener component is dedicated for creating process instance by listening to FOI topic
 * The topic is configurable through properties.
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Qualifier("foiRequestMessageListener")
@Component
public class FOIRequestMessageListener {

    @Autowired
    private FOIRequestMessageService foiRequestMessageService;

    @Autowired
    private ObjectMapper objectMapper;


    private final Logger LOGGER = Logger.getLogger(TaskEventMessageListener.class.getName());

    public void receiveMessage(String message) throws IOException {
        foiRequestMessageService.execute(createFOIRequestMessage(message));
    }


    private FOIRequestMessage createFOIRequestMessage(String message) throws JsonProcessingException {
        Map<String,Object> inMap = objectMapper.readValue(message, HashMap.class);
        FOIRequestMessage foiRequestMessage = new FOIRequestMessage();
        foiRequestMessage.setAttributes(inMap);
        foiRequestMessage.setProcessDefinitionKey(getProcessDefinitionKey());
        return foiRequestMessage;
    }

    private String getProcessDefinitionKey() { return "foi-request";}

}
