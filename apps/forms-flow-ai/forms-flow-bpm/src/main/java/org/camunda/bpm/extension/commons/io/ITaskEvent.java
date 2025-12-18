package org.camunda.bpm.extension.commons.io;

/**
 * This class defines the common functions of IO handling.
 *
 * @author sumathi.thirumani@aot-technologies.com
 */
public interface ITaskEvent {
    default String getTopicNameForTaskDetail() {  return "task-event-details"; }

    default String getTopicNameForTask() {  return "task-event"; }

    default String getExecutorName() { return "receiveMessage";}

}
