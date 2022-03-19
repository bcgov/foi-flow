<?xml version="1.0" encoding="UTF-8"?>
<WebServiceRequestEntity>
   <description></description>
   <name>FoiRawRequest</name>
   <tag></tag>
   <elementGuidId>2205eca3-b999-4e4d-b750-5eb0ebb68ab5</elementGuidId>
   <selectorMethod>BASIC</selectorMethod>
   <useRalativeImagePath>false</useRalativeImagePath>
   <connectionTimeout>0</connectionTimeout>
   <followRedirects>false</followRedirects>
   <httpBody></httpBody>
   <httpBodyContent>{
  &quot;text&quot;: &quot;{\n   \&quot;requestData\&quot;:{\n      \&quot;requestType\&quot;:{\n         \&quot;requestType\&quot;:\&quot;${requestType}\&quot;\n      },\n      \&quot;choose-idenity\&quot;:{\n         \&quot;answerYes\&quot;:null\n      },\n      \&quot;selectAbout\&quot;:{\n         \&quot;yourself\&quot;:true,\n         \&quot;child\&quot;:null,\n         \&quot;another\&quot;:null\n      },\n      \&quot;ministry\&quot;:{\n         \&quot;selectedMinistry\&quot;:[\n            {\n               \&quot;code\&quot;:\&quot;EDUC\&quot;,\n               \&quot;name\&quot;:\&quot;Education\&quot;,\n               \&quot;selected\&quot;:true\n            }\n         ],\n         \&quot;ministryPage\&quot;:\&quot;/personal/ministry-confirmation\&quot;,\n         \&quot;defaultMinistry\&quot;:{\n            \n         }\n      },\n      \&quot;contactInfo\&quot;:{\n         \&quot;firstName\&quot;:\&quot;${applicantFirstname}\&quot;,\n         \&quot;middleName\&quot;:null,\n         \&quot;lastName\&quot;:\&quot;${applicantLastname}\&quot;,\n         \&quot;alsoKnownAs\&quot;:null,\n         \&quot;businessName\&quot;:\&quot;${organization}\&quot;,\n         \&quot;birthDate\&quot;:\&quot;1990-12-04T08:00:00.000Z\&quot;\n      },\n      \&quot;requestTopic\&quot;:{\n         \&quot;value\&quot;:\&quot;anotherTopic\&quot;,\n         \&quot;text\&quot;:\&quot;Other\&quot;,\n         \&quot;ministryCode\&quot;:null\n      },\n      \&quot;descriptionTimeframe\&quot;:{\n         \&quot;description\&quot;:\&quot;${description}\&quot;,\n         \&quot;fromDate\&quot;:\&quot;2021-12-15T08:00:00.000Z\&quot;,\n         \&quot;toDate\&quot;:\&quot;2021-12-17T08:00:00.000Z\&quot;,\n         \&quot;correctionalServiceNumber\&quot;:null,\n         \&quot;publicServiceEmployeeNumber\&quot;:null,\n         \&quot;topic\&quot;:\&quot;Other\&quot;\n      },\n      \&quot;contactInfoOptions\&quot;:{\n         \&quot;email\&quot;:\&quot;${email}\&quot;,\n         \&quot;phonePrimary\&quot;:\&quot;${homePhone}\&quot;,\n         \&quot;phoneSecondary\&quot;:null,\n         \&quot;address\&quot;:null,\n         \&quot;city\&quot;:null,\n         \&quot;postal\&quot;:null,\n         \&quot;province\&quot;:null,\n         \&quot;country\&quot;:null\n      },\n      \&quot;Attachments\&quot;:[     \n      ]\n   }\n}&quot;,
  &quot;contentType&quot;: &quot;application/json&quot;,
  &quot;charset&quot;: &quot;UTF-8&quot;
}</httpBodyContent>
   <httpBodyType>text</httpBodyType>
   <httpHeaderProperties>
      <isSelected>true</isSelected>
      <matchCondition>equals</matchCondition>
      <name>Content-Type</name>
      <type>Main</type>
      <value>application/json</value>
   </httpHeaderProperties>
   <katalonVersion>8.2.0</katalonVersion>
   <maxResponseSize>0</maxResponseSize>
   <migratedVersion>5.4.1</migratedVersion>
   <restRequestMethod>POST</restRequestMethod>
   <restUrl>${URL}/api/foirawrequests</restUrl>
   <serviceType>RESTful</serviceType>
   <soapBody></soapBody>
   <soapHeader></soapHeader>
   <soapRequestMethod></soapRequestMethod>
   <soapServiceEndpoint></soapServiceEndpoint>
   <soapServiceFunction></soapServiceFunction>
   <socketTimeout>0</socketTimeout>
   <useServiceInfoFromWsdl>true</useServiceInfoFromWsdl>
   <variables>
      <defaultValue>GlobalVariable.api_domain</defaultValue>
      <description></description>
      <id>c86f6b10-7bf8-4340-9c67-baccef0e723f</id>
      <masked>false</masked>
      <name>URL</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('requestType', 1)</defaultValue>
      <description></description>
      <id>b5dc67a0-d8c8-4c32-8ae6-f0dc846c43cb</id>
      <masked>false</masked>
      <name>requestType</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('email', 1)</defaultValue>
      <description></description>
      <id>c0ac0737-58dc-41ec-b9ee-a9caca9083c4</id>
      <masked>false</masked>
      <name>email</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('streetAddress', 1)</defaultValue>
      <description></description>
      <id>0da15985-f430-434d-8b34-fe0c58c728c9</id>
      <masked>false</masked>
      <name>streetAddress</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('streetAddress2', 1)</defaultValue>
      <description></description>
      <id>61a765c5-cd22-4828-9b39-71abca853622</id>
      <masked>false</masked>
      <name>streetAddress2</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('city', 1)</defaultValue>
      <description></description>
      <id>484d5ac0-55e3-47fa-ba26-79ffb0160fff</id>
      <masked>false</masked>
      <name>city</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('province', 1)</defaultValue>
      <description></description>
      <id>868558a2-b7a7-490f-b19d-22c21b6ff4c0</id>
      <masked>false</masked>
      <name>province</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('country', 1)</defaultValue>
      <description></description>
      <id>3f0f7aac-be98-4404-ba68-f5c61b30365f</id>
      <masked>false</masked>
      <name>country</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('postalCode', 1)</defaultValue>
      <description></description>
      <id>87aa140d-8c85-4360-8957-f9de8fff3e62</id>
      <masked>false</masked>
      <name>postalCode</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('homePhone', 1)</defaultValue>
      <description></description>
      <id>b4c46111-2d10-4ac9-90c1-c18ee729c617</id>
      <masked>false</masked>
      <name>homePhone</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('description', 1)</defaultValue>
      <description></description>
      <id>43dff5f1-493e-474d-a085-1d194753eca7</id>
      <masked>false</masked>
      <name>description</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('applicantFirstname', 1)</defaultValue>
      <description></description>
      <id>1dd7afca-88e3-48e0-92db-ffd00c405f71</id>
      <masked>false</masked>
      <name>applicantFirstname</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('applicantLastname', 1)</defaultValue>
      <description></description>
      <id>42c0c76a-50b0-44fe-840c-473ff9200174</id>
      <masked>false</masked>
      <name>applicantLastname</name>
   </variables>
   <variables>
      <defaultValue>findTestData('Sample Applicant').getValue('organization', 1)</defaultValue>
      <description></description>
      <id>45e97791-e099-4128-9949-b4fcc97b003b</id>
      <masked>false</masked>
      <name>organization</name>
   </variables>
   <verificationScript>import static org.assertj.core.api.Assertions.*

import com.kms.katalon.core.testobject.RequestObject
import com.kms.katalon.core.testobject.ResponseObject
import com.kms.katalon.core.webservice.keyword.WSBuiltInKeywords as WS
import com.kms.katalon.core.webservice.verification.WSResponseManager

import groovy.json.JsonSlurper
import internal.GlobalVariable as GlobalVariable

RequestObject request = WSResponseManager.getInstance().getCurrentRequest()

ResponseObject response = WSResponseManager.getInstance().getCurrentResponse()</verificationScript>
   <wsdlAddress></wsdlAddress>
</WebServiceRequestEntity>
