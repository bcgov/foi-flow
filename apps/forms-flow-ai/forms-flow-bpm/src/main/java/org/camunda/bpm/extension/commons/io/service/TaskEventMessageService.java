package org.camunda.bpm.extension.commons.io.service;

import org.camunda.bpm.extension.commons.io.message.TaskMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;
import spinjar.com.fasterxml.jackson.core.JsonProcessingException;
import spinjar.com.fasterxml.jackson.databind.ObjectMapper;

import java.util.HashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * This component publishes the message to websocket
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Component
public class TaskEventMessageService {

    private final Logger LOGGER = Logger.getLogger(TaskEventMessageService.class.getName());

    @Autowired
    private SimpMessagingTemplate template;

    public void sendMessage(TaskMessage message) {
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            template.convertAndSend("/topic/task-event", objectMapper.writeValueAsString(message));
        } catch (JsonProcessingException e) {
            LOGGER.log(Level.SEVERE,"Exception Occured in preparing message", e);
        }
    }


}
