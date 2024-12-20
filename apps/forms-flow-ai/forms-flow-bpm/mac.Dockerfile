# Modified by Yichun Zhao and Walter Moar

# Maven build
FROM artifacts.developer.gov.bc.ca/docker-remote/maven:3.6.1-jdk-11-slim AS MAVEN_TOOL_CHAIN

RUN apt-get update \
    && apt-get install -y git

ARG FORMIO_SOURCE_REPO_BRANCH=v4.0.5-alpha
ARG FORMIO_SOURCE_REPO_URL=https://github.com/AOT-Technologies/forms-flow-ai.git

RUN git clone -b ${FORMIO_SOURCE_REPO_BRANCH} ${FORMIO_SOURCE_REPO_URL} /bpm/

#RUN cp /bpm/forms-flow-bpm/pom-docker.xml /tmp/pom.xml
#RUN cp /bpm/forms-flow-bpm/settings-docker.xml /usr/share/maven/ref/
COPY ./pom-docker.xml /tmp/pom.xml
COPY ./settings-docker.xml /usr/share/maven/ref/

WORKDIR /tmp/

# This allows Docker to cache most of the maven dependencies
RUN mvn -s /usr/share/maven/ref/settings-docker.xml dependency:resolve-plugins dependency:resolve dependency:go-offline -B
RUN rm -rf /bpm/forms-flow-bpm/src/main/resources/processes
RUN cp -r /bpm/forms-flow-bpm/src/ /tmp/src/

ARG CUSTOM_SRC_DIR=src/main/

# Override these files they have custom changes in the sbc_divapps directory
COPY ./${CUSTOM_SRC_DIR}/  /tmp/${CUSTOM_SRC_DIR}/
RUN mvn -s /usr/share/maven/ref/settings-docker.xml package -Dmaven.test.skip



# Final custom slim java image (for apk command see jdk-11.0.3_7-alpine-slim)
FROM --platform=amd64 artifacts.developer.gov.bc.ca/docker-remote/adoptopenjdk/openjdk11:jdk-11.0.3_7-alpine

ENV JAVA_VERSION jdk-11.0.3+7
ENV JAVA_HOME=/opt/java/openjdk \
    PATH="/opt/java/openjdk/bin:$PATH"

EXPOSE 8080
# OpenShift has /app in the image, but it's missing when doing local development - Create it when missing
RUN test ! -d /app && mkdir /app || :
# Add spring boot application
RUN mkdir -p /app
COPY --from=MAVEN_TOOL_CHAIN /tmp/target/forms-flow-bpm.jar ./app
RUN chmod a+rwx -R /app
WORKDIR /app
VOLUME /tmp
ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom","-jar","/app/forms-flow-bpm.jar"]