#!/bin/bash

# Check if /app-data is empty
if [ -z "$(ls -A /App-Data)" ]; then
  echo "App_Data directory is empty, copying files..."
  cp -r /app/App_Data/* /App-Data/
  echo "App_Data files copied."
  chmod -R 777 /App-Data/ # Change permissions after copy
else
  echo "App_Data directory is not empty, skipping copy."
  chmod -R 777 /App-Data/ # Change permissions even if no copy
fi