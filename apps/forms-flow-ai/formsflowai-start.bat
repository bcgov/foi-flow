@echo off

setlocal enableextensions enabledelayedexpansion

set REPO_URL=https://github.com/AOT-Technologies/forms-flow-ai.git
set REPO_BRANCH=v4.0.5-alpha
set FFA_WEB_DIRECTORY=%cd%/forms-flow-ai-web
set FFA_API_DIRECTORY=%cd%/forms-flow-api
set FFA_DIRECTORY=%FFA_WEB_DIRECTORY%/../v4.0.5-alpha

if exist "%FFA_WEB_DIRECTORY%/../v4.0.5-alpha" echo "Folder already exists" 
if not exist "%FFA_WEB_DIRECTORY%/../v4.0.5-alpha" echo "Folder does not exist", echo "Creating Directory for version 4.0.5-alpha"
if not exist "%FFA_WEB_DIRECTORY%/../v4.0.5-alpha" mkdir "%FFA_DIRECTORY%"

if not exist "%FFA_WEB_DIRECTORY%/../v4.0.5-alpha/forms-flow-web" (
echo "Clone formsflow.ai"
git clone -b %REPO_BRANCH% %REPO_URL% "%FFA_DIRECTORY%"
)
if exist "%FFA_WEB_DIRECTORY%/../v4.0.5-alpha/forms-flow-web" (
robocopy "%FFA_DIRECTORY%/forms-flow-web" "%FFA_WEB_DIRECTORY%" /E /XC /XN /XO /NP /NFL
)


docker-compose -f docker-compose.yml up --build -d forms-flow-forms
set /p choice=Is the role mapping variables provided in .env? [Y/N]
if '%choice%'=='Y' (
docker-compose -f docker-compose.yml up --build -d forms-flow-webapi forms-flow-web
) 
:end

