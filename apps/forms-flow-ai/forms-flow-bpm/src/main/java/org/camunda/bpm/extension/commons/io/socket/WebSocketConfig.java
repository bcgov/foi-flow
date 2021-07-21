package org.camunda.bpm.extension.commons.io.socket;


import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.event.EventListener;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.web.socket.config.annotation.*;
import org.springframework.web.socket.messaging.SessionConnectedEvent;
import org.springframework.web.socket.messaging.SessionDisconnectEvent;

import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Configuration for Message Broker
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    private final Logger LOGGER = Logger.getLogger(WebSocketConfig.class.getName());

    @Value("${websocket.security.origin}")
    private String websocketOrigin;


    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/forms-flow-bpm-socket").setAllowedOrigins(getOrigins())
                .withSockJS();
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config.enableSimpleBroker("/topic");
        config.setApplicationDestinationPrefixes("/camunda/forms-flow-bpm-socket");
    }

    @EventListener
    public void onSocketConnected(SessionConnectedEvent event) {
        StompHeaderAccessor sha = StompHeaderAccessor.wrap(event.getMessage());
        LOGGER.log(Level.INFO,"WebSocket Session Connected - sessionId :", sha.getSessionId());
    }

    @EventListener
    public void onSocketDisconnected(SessionDisconnectEvent event) {
        StompHeaderAccessor sha = StompHeaderAccessor.wrap(event.getMessage());
        LOGGER.log(Level.INFO,"WebSocket Session Disconnected - sessionId :", sha.getSessionId());
    }

    private String[] getOrigins() {
        if(StringUtils.isNotBlank(websocketOrigin)) {
            return websocketOrigin.split(",");
        }
        return new String[]{"*"};
    }
}