<?xml version="1.0" encoding="UTF-8"?>
<TestSuiteEntity>
   <description></description>
   <name>foi-test-homepage-and-login</name>
   <tag></tag>
   <isRerun>false</isRerun>
   <mailRecipient></mailRecipient>
   <numberOfRerun>3</numberOfRerun>
   <pageLoadTimeout>30</pageLoadTimeout>
   <pageLoadTimeoutDefault>true</pageLoadTimeoutDefault>
   <rerunFailedTestCasesOnly>false</rerunFailedTestCasesOnly>
   <rerunImmediately>true</rerunImmediately>
   <testSuiteGuid>ee645f36-b53d-42bf-9904-d8c7fedab02b</testSuiteGuid>
   <testCaseLink>
      <guid>757ce485-35ab-4fb4-9ddf-0393e3262908</guid>
      <isReuseDriver>false</isReuseDriver>
      <isRun>true</isRun>
      <testCaseId>Test Cases/login/foi-test-homepage</testCaseId>
   </testCaseLink>
   <testCaseLink>
      <guid>849fee5a-4ea5-40e1-a9bd-73d93b36c58d</guid>
      <isReuseDriver>false</isReuseDriver>
      <isRun>true</isRun>
      <testCaseId>Test Cases/login/foi-test-login-page</testCaseId>
   </testCaseLink>
   <testCaseLink>
      <guid>11e100b1-804b-4bbb-bcd1-597d43da7e2c</guid>
      <isReuseDriver>false</isReuseDriver>
      <isRun>true</isRun>
      <testCaseId>Test Cases/login/foi-test-valid-login-content</testCaseId>
      <testDataLink>
         <combinationType>ONE</combinationType>
         <id>e425cd71-6d16-42bb-b4f6-3fb84e6d65d1</id>
         <iterationEntity>
            <iterationType>ALL</iterationType>
            <value></value>
         </iterationEntity>
         <testDataId>Data Files/Login Credentials</testDataId>
      </testDataLink>
      <variableLink>
         <testDataLinkId>e425cd71-6d16-42bb-b4f6-3fb84e6d65d1</testDataLinkId>
         <type>DATA_COLUMN</type>
         <value>Username</value>
         <variableId>94827f55-a251-4025-9719-11c192cf9bf1</variableId>
      </variableLink>
      <variableLink>
         <testDataLinkId>e425cd71-6d16-42bb-b4f6-3fb84e6d65d1</testDataLinkId>
         <type>DATA_COLUMN</type>
         <value>Password</value>
         <variableId>9f013253-ef8b-4088-ac4e-034a93f87198</variableId>
      </variableLink>
      <variableLink>
         <testDataLinkId>e425cd71-6d16-42bb-b4f6-3fb84e6d65d1</testDataLinkId>
         <type>DATA_COLUMN</type>
         <value>First Name</value>
         <variableId>c97fd75e-a2ad-42ab-9bbd-d9dc42260a7d</variableId>
      </variableLink>
      <variableLink>
         <testDataLinkId>e425cd71-6d16-42bb-b4f6-3fb84e6d65d1</testDataLinkId>
         <type>DATA_COLUMN</type>
         <value>Last Name</value>
         <variableId>ed9c7b40-9cee-4260-9823-ac9df645252f</variableId>
      </variableLink>
   </testCaseLink>
   <testCaseLink>
      <guid>fa5a5d4e-7bbe-4075-9cdd-b8824000bdd9</guid>
      <isReuseDriver>false</isReuseDriver>
      <isRun>true</isRun>
      <testCaseId>Test Cases/login/foi-test-invalid-login-credentials</testCaseId>
      <variableLink>
         <testDataLinkId></testDataLinkId>
         <type>DEFAULT</type>
         <value></value>
         <variableId>efa27612-a98e-48ac-afc2-57f8ec888808</variableId>
      </variableLink>
   </testCaseLink>
   <testCaseLink>
      <guid>c8054c8b-8556-4bb5-9c72-d9373c9c19a9</guid>
      <isReuseDriver>false</isReuseDriver>
      <isRun>true</isRun>
      <testCaseId>Test Cases/login/foi-test-sign-out</testCaseId>
   </testCaseLink>
</TestSuiteEntity>
