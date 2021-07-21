package org.camunda.bpm.extension.commons.io.socket;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.StringRedisTemplate;


import java.util.Properties;

/**
 * Configuration for Message Broker.
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Configuration
public class RedisConfig {

    @Autowired
    private Properties messageBrokerProperties;

    @Bean
    RedisConnectionFactory redisConnectionFactory() {
        RedisStandaloneConfiguration redisStandaloneConfiguration = new RedisStandaloneConfiguration(messageBrokerProperties.getProperty("messageBroker.host"),
                Integer.valueOf(messageBrokerProperties.getProperty("messageBroker.port")));
        redisStandaloneConfiguration.setPassword(messageBrokerProperties.getProperty("messageBroker.passcode"));
        return new LettuceConnectionFactory(redisStandaloneConfiguration);
    }

   @Bean
    StringRedisTemplate template(RedisConnectionFactory redisConnectionFactory) {
        return new StringRedisTemplate(redisConnectionFactory);
    }

    protected Properties getMessageBrokerProperties() {
        return messageBrokerProperties;
    }



}
