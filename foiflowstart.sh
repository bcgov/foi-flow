
#!/bin/sh
setlocal enableextensions enabledelayedexpansion

REPO_URL=https://github.com/AOT-Technologies/forms-flow-ai.git
REPO_BRANCH=v4.0.5-alpha
START_REDIS=N
BPM_DIRECTORY=apps/forms-flow-ai/forms-flow-bpm
FFA_WEB_DIRECTORY=%cd%/apps/forms-flow-ai/forms-flow-ai-web
FFA_DIRECTORY=${BPM_DIRECTORY}/${REPO_BRANCH}


echo 'hello world'

echo $REPO_URL




if [ -d  "${BPM_DIRECTORY}/${REPO_BRANCH}" ] 
then 
    echo "Folder already exists" 
else 
    echo "BPM Folder NOT  exists" 
    sudo mkdir -p $FFA_DIRECTORY
    chmod 777 $FFA_DIRECTORY
    echo "created folder path ${FFA_DIRECTORY}"
    echo "Clone formsflow.ai"
    git clone -b $REPO_BRANCH $REPO_URL $FFA_DIRECTORY
fi

if [ -d "${BPM_DIRECTORY}/${REPO_BRANCH}/forms-flow-bpm" ]
then 
    echo "Removing addition files from ${FFA_DIRECTORY}/forms-flow-bpm/src/main/resources/processes"
    rm  -r "${FFA_DIRECTORY}/forms-flow-bpm/src/main/resources/processes"   
    cp -uaT "${FFA_DIRECTORY}/forms-flow-bpm/src" "${BPM_DIRECTORY}/src"
fi   
