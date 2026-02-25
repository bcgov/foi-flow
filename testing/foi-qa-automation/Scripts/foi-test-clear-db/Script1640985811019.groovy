import com.katalon.plugin.keyword.connection.DBType

import internal.GlobalVariable as GlobalVariable

def connection

def query = 'delete FROM public."FOIRawRequestComments" ;' +
'delete FROM public."FOIRawRequestDocuments" ;' +
'delete FROM public."FOIRawRequestNotificationUsers" ;' +
'delete FROM public."FOIRawRequestNotifications" ;' +
'delete FROM public."FOIRawRequestWatchers" ;' + 
'delete FROM public."FOIRawRequests" ;' +
'delete FROM public."FOIRequestApplicantMappings" ;' +
'delete FROM public."FOIRequestContactInformation" ;' +
'delete FROM public."FOIRequestComments" ;' +
'delete FROM public."FOIMinistryRequestDivisions" ;' +
'delete FROM public."FOIMinistryRequestDocuments" ;' +
'delete FROM public."FOIRequestNotificationUsers" ;' +  
'delete FROM public."FOIRequestNotifications" ;' +
'delete FROM public."FOIRequestWatchers" ;' +
'delete FROM public."FOIMinistryRequests" ;' +
'delete FROM public."FOIRequests" ' 

connection = CustomKeywords.'com.katalon.plugin.keyword.connection.DatabaseKeywords.createConnection'(DBType.postgresql, GlobalVariable.db_domain, GlobalVariable.db_port, GlobalVariable.db_name, GlobalVariable.db_username, GlobalVariable.db_password)
connection.setAutoCommit(false)
CustomKeywords.'com.katalon.plugin.keyword.connection.DatabaseKeywords.execute'(connection, query)

CustomKeywords.'com.katalon.plugin.keyword.connection.DatabaseKeywords.closeConnection'(connection)