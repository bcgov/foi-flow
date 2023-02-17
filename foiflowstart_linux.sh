
#!/bin/sh
setlocal enableextensions enabledelayedexpansion

REPO_URL=https://github.com/AOT-Technologies/forms-flow-ai.git
REPO_BRANCH=v4.0.5-alpha
START_REDIS=N
FFA_APPS_ROOT=apps/forms-flow-ai
BPM_DIRECTORY=apps/forms-flow-ai/forms-flow-bpm
FFA_REPO_DIRECTORY=${FFA_APPS_ROOT}/${REPO_BRANCH}
FFA_WEB_DIRECTORY="${FFA_APPS_ROOT}/forms-flow-ai-web"

echo 'hello world'

echo $REPO_URL




if [ -d  "${FFA_REPO_DIRECTORY}" ] 
then 
    echo "Folder already exists" 
else 
    echo "BPM Folder NOT  exists" 
    sudo mkdir -p $FFA_REPO_DIRECTORY
    chmod 777 -R $FFA_REPO_DIRECTORY
    echo "created folder path ${FFA_REPO_DIRECTORY}"
    echo "Clone formsflow.ai"
    git clone -b $REPO_BRANCH $REPO_URL $FFA_REPO_DIRECTORY
fi
chmod 777 -R $FFA_REPO_DIRECTORY
if [ -d "${FFA_REPO_DIRECTORY}/forms-flow-bpm" ]
then 
    echo "Removing addition files from ${FFA_DIRECTORY}/forms-flow-bpm/src/main/resources/processes"
    rm  -r "${FFA_REPO_DIRECTORY}/forms-flow-bpm/src/main/resources/processes"   
    cp -uaT "${FFA_REPO_DIRECTORY}/forms-flow-bpm/src" "${BPM_DIRECTORY}/src"
fi   

if [ -d "${FFA_REPO_DIRECTORY}/forms-flow-web" ]
then 
    
    cp -uaT "${FFA_REPO_DIRECTORY}/forms-flow-web" $FFA_WEB_DIRECTORY
fi   

