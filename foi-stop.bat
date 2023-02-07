@echo off


setlocal enableextensions enabledelayedexpansion

set FFA_DIRECTORY=%cd%/apps/forms-flow-ai
set NOTIFICATION_DIRECTORY=%cd%/notification-manager
set /p stopall=Do you wish to stop all containers? [Y/N]
if /I '%stopall%'=='Y' (
docker-compose -f docker-compose.yml down
docker-compose -f %FFA_DIRECTORY%/docker-compose.yml stop forms-flow-forms forms-flow-forms-db forms-flow-webapi forms-flow-webapi-db forms-flow-web
	docker-compose -f %NOTIFICATION_DIRECTORY%/docker-compose.yml down

) 
if /I '%stopall%'=='N' (
set /P servicenames="Enter services(s) here (ex: web, api, bpm, redis, ffa) separated by space?"
(for %%a in (!servicenames!) do ( 
   if /I %%a == bpm ( 
	echo "Stopping BPM..."
	docker-compose -f docker-compose.yml stop forms-flow-bpm forms-flow-bpm-db  
   )
   if /I %%a == api ( 
	echo "Stopping API..."
	docker-compose -f docker-compose.yml stop BACKEND foi-requests-DB
   )
   if /I %%a == web ( 
	echo "Stopping Web..."
	docker-compose -f docker-compose.yml stop foi-web
   )
   if /I %%a == ffa ( 
	echo "Stopping forms-flow-ai..."
	docker-compose -f %FFA_DIRECTORY%/docker-compose.yml stop forms-flow-forms forms-flow-forms-db forms-flow-webapi forms-flow-webapi-db forms-flow-web
   )
   if /I %%a == redis ( 
	echo "Stopping Redis..."
	docker-compose -f docker-compose.yml stop foiredis 
   )
   
))

)
:end
