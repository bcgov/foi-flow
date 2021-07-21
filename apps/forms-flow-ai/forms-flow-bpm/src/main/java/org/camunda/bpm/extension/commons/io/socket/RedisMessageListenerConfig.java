package org.camunda.bpm.extension.commons.io.socket;

import org.camunda.bpm.extension.commons.io.ITaskEvent;
import org.camunda.bpm.extension.commons.io.listener.TaskEventMessageListener;
import org.camunda.bpm.extension.commons.io.listener.spi.FOIRequestMessageListener;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.listener.PatternTopic;
import org.springframework.data.redis.listener.RedisMessageListenerContainer;
import org.springframework.data.redis.listener.adapter.MessageListenerAdapter;

import java.util.logging.Logger;

/**
 * This configuration class consolidates all message listeners.
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Configuration
public class RedisMessageListenerConfig extends RedisConfig implements ITaskEvent {

    private final Logger LOGGER = Logger.getLogger(RedisMessageListenerConfig.class.getName());

    @Bean
    RedisMessageListenerContainer container(RedisConnectionFactory connectionFactory,
                                            @Qualifier("taskMessageListenerAdapter") MessageListenerAdapter taskMessageListenerAdapter,
                                            @Qualifier("foiMessageListenerAdapter") MessageListenerAdapter foiMessageListenerAdapter) {
        RedisMessageListenerContainer container = new RedisMessageListenerContainer();
        container.setConnectionFactory(connectionFactory);
        container.addMessageListener(taskMessageListenerAdapter, new PatternTopic(getTopicNameForTask()));
        container.addMessageListener(foiMessageListenerAdapter, new PatternTopic(getTopicNameForFOIRequest()));
        return container;
    }


    @Bean("taskMessageListenerAdapter")
    MessageListenerAdapter taskMessageListenerAdapter(TaskEventMessageListener taskEventMessageListener) {
        return new MessageListenerAdapter(taskEventMessageListener, getExecutorName());
    }

    @Bean("foiMessageListenerAdapter")
    MessageListenerAdapter foiMessageListenerAdapter(FOIRequestMessageListener foiRequestMessageListener) {
        return new MessageListenerAdapter(foiRequestMessageListener, getExecutorName());
    }

    private String getTopicNameForFOIRequest() {return getMessageBrokerProperties().getProperty("plugin.foi.rawRequest-topic");}

}
