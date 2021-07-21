package org.camunda.bpm.extension.commons.io.message.spi;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.ToString;

import java.io.Serializable;
import java.util.Map;

/**
 * Generic FOI Request Message Definition.
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
@Data
@NoArgsConstructor
@ToString
public class FOIRequestMessage implements Serializable {
    private Map<String,Object> attributes;
    private String processDefinitionKey;

}
