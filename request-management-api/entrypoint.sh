#!/bin/bash


[ ! -f .env ] || export $(grep -v '^#' .env | xargs)

if [[ $DEBUG_MODE="ON" ]]
then
    python manage.py db && flask run -h 0.0.0.0 -p 5000
else
    python manage.py db upgrade && python wsgi.py
fi