package org.camunda.bpm.extension.commons.io.event;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.lang3.StringUtils;
import org.camunda.bpm.engine.delegate.DelegateTask;
import org.camunda.bpm.extension.commons.io.ITaskEvent;
import org.camunda.bpm.extension.commons.io.message.TaskEventMessage;
import org.camunda.bpm.extension.commons.io.message.TaskMessage;
import org.springframework.beans.BeanUtils;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.event.EventListener;


import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.util.*;

import java.util.logging.Logger;

/**
 * This class intercepts all camunda task and push socket messages for web tier updates.
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Component
public class CamundaEventListener implements ITaskEvent {

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    private final Logger LOGGER = Logger.getLogger(CamundaEventListener.class.getName());

    @Value("${websocket.messageType}")
    private String messageCategory;


    @EventListener
    public void onTaskEventListener(DelegateTask taskDelegate) {
        LOGGER.info("Event triggered:"+taskDelegate.getId() +"-"+ taskDelegate.getEventName() + "-"+ taskDelegate.getProcessInstanceId());
        try {
            if(isAllowed(EventCategory.TASK_EVENT_DETAILS.name())) {
                this.stringRedisTemplate.convertAndSend(getTopicNameForTaskDetail(),  getObjectMapper().writeValueAsString(getTaskMessage(taskDelegate)));
            }
            if(isAllowed(EventCategory.TASK_EVENT.name())) {
                this.stringRedisTemplate.convertAndSend(getTopicNameForTask(),  getObjectMapper().writeValueAsString(getTaskEventMessage(taskDelegate)));
             }
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }
    }

     private TaskMessage getTaskMessage(DelegateTask taskDelegate) {
        TaskMessage taskObj = new TaskMessage();
        BeanUtils.copyProperties(taskDelegate, taskObj);
        taskObj.setVariables(getVariables(taskDelegate));
        return taskObj;
    }

    private TaskEventMessage getTaskEventMessage(DelegateTask taskDelegate) {
        TaskEventMessage taskObj = new TaskEventMessage();
        BeanUtils.copyProperties(taskDelegate, taskObj);
        return taskObj;
    }

    private boolean isAllowed(String category) {
        return Arrays.asList(StringUtils.split(messageCategory,",")).contains(category);
    }

    private Map<String,Object> getVariables(DelegateTask taskDelegate) {
        List<String> configMap =getElements();
        Map<String,Object> variables = new HashMap<>();
        for(String entry : configMap) {
            if(taskDelegate.getVariables().containsKey(entry)) {
                variables.put(entry, taskDelegate.getVariable(entry));
            }
        }
        return variables;
    }

    private List<String> getElements() {
        return new ArrayList<>(Arrays. asList("applicationId", "formUrl", "applicationStatus"));
    }

    private ObjectMapper getObjectMapper() {
        return new ObjectMapper();
    }

    enum EventCategory {
        TASK_EVENT,
        TASK_EVENT_DETAILS;
    }

}
