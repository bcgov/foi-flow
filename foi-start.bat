@echo off

setlocal enableextensions enabledelayedexpansion

set REPO_URL=https://github.com/AOT-Technologies/forms-flow-ai.git
set REPO_BRANCH=RC4.0.2
SET START_REDIS=N
set BPM_DIRECTORY=%cd%/apps/forms-flow-ai/forms-flow-bpm
set FFA_DIRECTORY=%BPM_DIRECTORY%/../rc4.0.2


if exist "%BPM_DIRECTORY%/../rc4.0.2" echo "Folder already exists" 
if not exist "%BPM_DIRECTORY%/../rc4.0.2" echo "Folder does not exist", echo "Creating Directory for version 4.0.2"
if not exist "%BPM_DIRECTORY%/../rc4.0.2" mkdir "%FFA_DIRECTORY%"

if not exist "%BPM_DIRECTORY%/../rc4.0.2/forms-flow-bpm" (
echo "Clone formsflow.ai"
git clone -b %REPO_BRANCH% %REPO_URL% "%FFA_DIRECTORY%"
)
if exist "%BPM_DIRECTORY%/../rc4.0.2/forms-flow-bpm" (
rem Remove formio specific processes
rmdir "%FFA_DIRECTORY%/forms-flow-bpm/src/main/resources/processes" /q /s
robocopy "%FFA_DIRECTORY%/forms-flow-bpm/src" "%BPM_DIRECTORY%/src" /E /XC /XN /XO /NP /NFL
)

set /p choice=Do you want to start all containers? [Y/N]
if '%choice%'=='Y' (
docker-compose -f docker-compose.yml up --build -d
) 
if /I '%choice%'=='N' (
   
set /P servicenames="Enter services(s) here (ex: web, api, bpm) separated by space?"
(for %%a in (!servicenames!) do ( 
   if /I %%a == bpm ( 
	echo "Starting BPM..."
	SET START_REDIS=Y
	docker-compose -f docker-compose.yml up --build -d forms-flow-bpm
   )
   if /I %%a == api ( 
	echo "Starting API..."
	SET START_REDIS=Y
	docker-compose -f docker-compose.yml up --build -d BACKEND
   )
   if /I %%a == web ( 
	echo "Starting Web..."
	docker-compose -f docker-compose.yml up --build -d forms-flow-web
   )
   if !START_REDIS! == Y ( 
	echo "Starting Redis..."
	docker-compose -f docker-compose.yml up --build -d foiredis
   )
   
))


)

:end