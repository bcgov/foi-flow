package org.camunda.bpm.extension.commons.io.listener;

import org.camunda.bpm.extension.commons.io.service.TaskEventMessageService;
import org.camunda.bpm.extension.commons.io.message.TaskMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;
import spinjar.com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.logging.Logger;

/**
 * This component listens to message topic
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Qualifier("taskEventMessageListener")
@Component
public class TaskEventMessageListener {

    @Autowired
    private TaskEventMessageService taskEventMessageService;

    private final Logger LOGGER = Logger.getLogger(TaskEventMessageListener.class.getName());

    public void receiveMessage(String message) throws IOException {
        ObjectMapper objectMapper = new ObjectMapper();
        TaskMessage taskMessage = objectMapper.readValue(message, TaskMessage.class);
        taskEventMessageService.sendMessage(taskMessage);
    }
}
