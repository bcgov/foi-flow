@echo off


setlocal enableextensions enabledelayedexpansion
set FFA_WEB_DIRECTORY=%cd%/forms-flow-ai-web
set FFA_DIRECTORY=%FFA_WEB_DIRECTORY%/../v4.0.5-alpha

docker-compose -f docker-compose.yml stop forms-flow-forms forms-flow-forms-db forms-flow-webapi forms-flow-webapi-db forms-flow-web

:end
